import logging
import json
from django.core.serializers.json import DjangoJSONEncoder
import pyarrow.parquet as pq
from rate_tracker.constants import IngestRawStatus
from rates.models import IngestRaw
from .base import Source

logger = logging.getLogger("api_logger")


def ingest_parquet(source_obj: Source):
    """
    Reads a Parquet file chunk by chunk and performs bulk create operations.
    Uses response_id for idempotency.
    """
    try:
        parquet_file = pq.ParquetFile(source_obj.source)
        total_rows = 0
        batch_count = 0

        # Read in batches of 10,000 to keep memory usage low
        for batch in parquet_file.iter_batches(batch_size=10_000):
            # Convert batch to list of dictionaries
            data_list = batch.to_pylist()
            raw_records = []

            for row_data in data_list:
                # Handle non-serializable types like datetime.date
                row_data = json.loads(json.dumps(row_data, cls=DjangoJSONEncoder))

                # Deterministic ID for idempotency:
                raw_res_id = str(row_data.get("raw_response_id", "unknown"))

                raw_records.append(
                    IngestRaw(
                        source=source_obj.name,
                        status=IngestRawStatus.PENDING,
                        response_id=raw_res_id,
                        data=row_data,
                    )
                )

            # Use ignore_conflicts=True to satisfy the idempotency requirement
            # Records with the same response_id will NOT be re-inserted or cause errors
            IngestRaw.objects.bulk_create(raw_records, ignore_conflicts=True)

            # Since ignore_conflicts=True is used, the returned result's PKs might be missing for skipped rows
            # but that's fine as we are only inserting.

            total_rows += len(raw_records)
            batch_count += 1
            logger.info(
                f"Processed batch {batch_count} ({len(raw_records)} rows) from {source_obj.name}"
            )

        logger.info(
            f"Parquet ingestion complete: {total_rows} rows processed from {source_obj.name}"
        )
        return {"status": "success", "total_rows_processed": total_rows}

    except Exception as e:
        logger.error(f"Parquet ingestion failed: {str(e)}")
        raise e
