from celery import shared_task
from rates.utils.ingestion_worker import IngestionWorker, Source
from django.core.management import call_command


@shared_task
def run_seed_data_task():
    """
    Periodic task to trigger the seed_data management command every hour.
    """
    call_command("seed_data")



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
def validation_task(self):
    """
    Step 2: Data Validation.
    """
    try:
        return IngestionWorker.validation_worker()
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def organizer_task(self):
    """
    Step 3: Data Organization (Rate Table Population).
    """
    try:
        return IngestionWorker.organizer_worker()
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)
