import logging
from .base import Source

logger = logging.getLogger("api_logger")


def ingest_socket(source_obj: Source):
    """
    Dummy function for socket ingestion.
    """
    msg = f"Socket ingestion for {source_obj.name} (source: {source_obj.source}) is not yet implemented."
    logger.info(msg)
    return {"status": "skipped", "message": msg}
