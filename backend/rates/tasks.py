from celery import shared_task, chain
from rates.utils.ingestion_worker import IngestionWorker, Source


@shared_task(bind=True)
def ingest_task(self, source_dict):
    """
    Step 1: Raw Data Ingestion.
    """
    try:
        source_obj = Source(**source_dict)
        return IngestionWorker.ingest(source_obj)
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def validation_task(self, prev_result=None):
    """
    Step 2: Data Validation.
    """
    try:
        return IngestionWorker.validation_worker()
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def organizer_task(self, prev_result=None):
    """
    Step 3: Data Organization (Rate Table Population).
    """
    try:
        return IngestionWorker.organizer_worker()
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def cleanup_task(self, prev_result=None):
    """
    Step 4: Cleanup processed raw data.
    """
    try:
        return IngestionWorker.cleanup_worker()
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def ingest_data_smoke_test(self):
    """
    Simple smoke test for Celery configuration.
    """
    try:
        return IngestionWorker.test()
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=3)
