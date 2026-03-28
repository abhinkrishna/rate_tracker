import logging
from django.db import transaction, connection
from django.utils import timezone
from rate_tracker.constants import IngestRawStatus
from rates.models import IngestRaw, Rate, Provider, Currency, RateType

# Import handlers and Source class
from .sources.base import Source
from .sources.parquet import ingest_parquet
from .sources.api import ingest_api
from .sources.scrap import ingest_scrap
from .sources.socket import ingest_socket
from .validators.rate_validator import RateValidator

logger = logging.getLogger("api_logger")


class IngestionWorker:
    @staticmethod
    def ingest(source_obj: Source):
        """
        Main entry point for saving raw data.
        Accepts a Source object and handles ingestion based on its type.
        """
        source_type = source_obj.type
        logger.info(
            f"Starting ingestion for source: {source_obj.name} (Type: {source_type})"
        )

        try:
            if source_type == "parquet":
                return ingest_parquet(source_obj)
            elif source_type == "api":
                return ingest_api(source_obj)
            elif source_type == "scrap":
                return ingest_scrap(source_obj)
            elif source_type == "socket":
                return ingest_socket(source_obj)
            else:
                raise ValueError(f"Unknown source type: {source_type}")
        except Exception as e:
            logger.error(f"Ingestion failed for {source_obj.name}: {str(e)}")
            raise e

    @staticmethod
    def validation_worker(chunk_size=10000):
        """
        Processes pending IngestRaw records and validates them in chunks.
        Checks if data structure matches the Rate table requirement.
        """
        logger.info("Starting validation worker with pagination...")

        total_pending = IngestRaw.objects.filter(status=IngestRawStatus.PENDING).count()
        logger.info(f"Total pending records to validate: {total_pending}")

        processed_count = 0
        failed_count = 0

        # We process in a loop until no more pending records are found
        # Each batch is updated, so they are removed from the 'pending' filter in the next iteration
        while True:
            batch = list(
                IngestRaw.objects.filter(status=IngestRawStatus.PENDING)[:chunk_size]
            )
            if not batch:
                break

            validated_records = []
            failed_records = []

            for record in batch:
                # Using separate RateValidator class
                if RateValidator.is_valid(record.data):
                    record.status = IngestRawStatus.VALIDATED
                    validated_records.append(record)
                    processed_count += 1
                else:
                    record.status = IngestRawStatus.FAILED
                    failed_records.append(record)
                    failed_count += 1

            # Using bulk_update to minimize database hits
            if validated_records:
                IngestRaw.objects.bulk_update(validated_records, ["status"])
            if failed_records:
                IngestRaw.objects.bulk_update(failed_records, ["status"])

            logger.info(
                f"Validation progress: Processed {processed_count + failed_count}/{total_pending} records..."
            )

        logger.info(
            f"Validation complete: {processed_count} validated, {failed_count} failed"
        )
        return {"validated": processed_count, "failed": failed_count}

    @staticmethod
    def _normalize_alias(name: str) -> str:
        """Helper to compute normalized aliases."""
        if not name:
            return ""
        return str(name).strip().lower().replace(" ", "_")

    @staticmethod
    def organizer_worker(chunk_size=1000):
        """
        Processes validated IngestRaw records, transforms them into Rate objects.
        Changes IngestRaw status to 'remove' after processing.
        Uses pagination and bulk creation.
        """
        logger.info("Starting organizer worker with pagination...")

        total_validated = IngestRaw.objects.filter(
            status=IngestRawStatus.VALIDATED
        ).count()
        logger.info(f"Total records to organize: {total_validated}")

        processed_count = 0

        # Simple caches for related objects to minimize redundant Lookups within one execution
        provider_cache = {}
        currency_cache = {}
        rate_type_cache = {}

        # Prepopulate caches
        for provider in Provider.objects.all():
            for alias in provider.aliases:
                provider_cache[alias] = provider
            provider_cache[IngestionWorker._normalize_alias(provider.name)] = provider

        for rt in RateType.objects.all():
            for alias in rt.aliases:
                rate_type_cache[alias] = rt
            rate_type_cache[IngestionWorker._normalize_alias(rt.name)] = rt

        for currency in Currency.objects.all():
            currency_cache[currency.code] = currency

        while True:
            batch = list(
                IngestRaw.objects.filter(status=IngestRawStatus.VALIDATED)[:chunk_size]
            )
            if not batch:
                break

            rates_to_create = []

            try:
                with transaction.atomic():
                    for record in batch:
                        data_items = (
                            record.data
                            if isinstance(record.data, list)
                            else [record.data]
                        )

                        for item in data_items:
                            # 1. Resolve Provider
                            raw_p_name = item.get("provider", "Unknown")
                            p_alias = IngestionWorker._normalize_alias(raw_p_name)
                            if p_alias not in provider_cache:
                                provider, created = Provider.objects.get_or_create(
                                    name=raw_p_name
                                )
                                if created:
                                    provider.aliases = [p_alias]
                                    provider.save(update_fields=["aliases"])
                                elif p_alias not in provider.aliases:
                                    provider.aliases.append(p_alias)
                                    provider.save(update_fields=["aliases"])
                                provider_cache[p_alias] = provider

                            # 2. Resolve Currency
                            c_code = item.get("currency", "USD")
                            if c_code not in currency_cache:
                                currency, _ = Currency.objects.get_or_create(
                                    code=c_code,
                                    defaults={
                                        "name": item.get("currency", "US Dollar")
                                    },
                                )
                                currency_cache[c_code] = currency

                            # 3. Resolve RateType
                            raw_rt_name = item.get("rate_type", "Standard")
                            rt_alias = IngestionWorker._normalize_alias(raw_rt_name)
                            if rt_alias not in rate_type_cache:
                                rate_type, created = RateType.objects.get_or_create(
                                    name=raw_rt_name
                                )
                                if created:
                                    rate_type.aliases = [rt_alias]
                                    rate_type.save(update_fields=["aliases"])
                                elif rt_alias not in rate_type.aliases:
                                    rate_type.aliases.append(rt_alias)
                                    rate_type.save(update_fields=["aliases"])
                                rate_type_cache[rt_alias] = rate_type

                            rates_to_create.append(
                                Rate(
                                    provider=provider_cache[p_alias],
                                    currency=currency_cache[c_code],
                                    rate_type=rate_type_cache[rt_alias],
                                    rate_value=item.get("rate_value", 0),
                                    effective_date=item.get(
                                        "effective_date", timezone.now().date()
                                    ),
                                    ingestion_ts=item.get(
                                        "ingestion_ts", timezone.now()
                                    ),
                                    source_url=item.get("source_url", ""),
                                    raw_response_id=record.response_id,
                                )
                            )

                        record.status = IngestRawStatus.REMOVE

                    # Perform bulk creation of rates for this batch
                    if rates_to_create:
                        Rate.objects.bulk_create(rates_to_create)

                    # Bulk update the IngestRaw status
                    IngestRaw.objects.bulk_update(batch, ["status"])

                    processed_count += len(batch)
                    logger.info(
                        f"Organization progress: Processed {processed_count}/{total_validated}..."
                    )

            except Exception as e:
                logger.error(f"Organization failed at batch level: {str(e)}")
                raise e

        logger.info(
            f"Organization complete: {processed_count} records processed into Rates table."
        )
        return {"organized": processed_count}

    @staticmethod
    def cleanup_worker():
        """
        Deletes IngestRaw records with status 'remove' using direct SQL for efficiency.
        This avoids Django's memory overhead by working entirely at the DB level.
        """
        logger.info("Starting cleanup worker using direct SQL...")

        # 1. Get the current count for reporting
        count = IngestRaw.objects.filter(status=IngestRawStatus.REMOVE).count()

        if count > 0:
            # Use dynamically retrieved table name for robustness
            table_name = IngestRaw._meta.db_table
            with connection.cursor() as cursor:
                # Direct SQL execution for maximum speed and zero memory allocation in Python
                # This bypasses all Django signals/cascades for performance.
                query = f"DELETE FROM {table_name} WHERE status = %s"
                cursor.execute(query, [IngestRawStatus.REMOVE])

            logger.info(f"Cleanup complete: {count} records removed from {table_name}")
        else:
            logger.info("No records found with 'remove' status. Cleanup skipped.")

        return {"deleted": count}

    @staticmethod
    def test():
        # Smoke test for Celery
        from django.contrib.auth import get_user_model

        User = get_user_model()
        total = 0
        for i in range(1_000):
            total += i
        user_count = User.objects.count()
        return {
            "status": "success",
            "sum": total,
            "user_count": user_count,
        }
