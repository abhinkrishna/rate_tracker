import logging
from .base import Source

logger = logging.getLogger("api_logger")


def ingest_scrap(source_obj: Source):
    """
    Dummy function for web scraper ingestion.
    """
    msg = f"Web Scraper ingestion for {source_obj.name} (source: {source_obj.source}) is not yet implemented."
    logger.info(msg)
    return {"status": "skipped", "message": msg}
