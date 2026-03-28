import hashlib
import json
import logging
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
        for batch in parquet_file.iter_batches(batch_size=10000):
            # Convert batch to list of dictionaries
            data_list = batch.to_pylist()
            raw_records = []

            for row_data in data_list:
                # Deterministic ID for idempotency:
                # Combine raw_response_id with a hash of the row's content

                raw_res_id = str(row_data.get("raw_response_id", "unknown"))

                # We sort keys and use a standard encoder to ensure consistent hashing
                data_string = json.dumps(row_data, sort_keys=True, default=str)
                data_hash = hashlib.md5(data_string.encode()).hexdigest()

                # This response_id should uniquely identify this data point across re-runs
                response_id = f"{raw_res_id}_{data_hash}"

                # Convert the cleanly stringified data back to dict so Django can save it safely as JSON
                clean_row_data = json.loads(data_string)

                raw_records.append(
                    IngestRaw(
                        source=source_obj.name,
                        status=IngestRawStatus.PENDING,
                        response_id=response_id[:255],
                        data=clean_row_data,
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
