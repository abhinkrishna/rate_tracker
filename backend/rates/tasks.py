from rates.utils import IngestionWorker
from celery import shared_task


@shared_task(bind=True)
def ingest_data_smoke_test(self):
    try:
        return IngestionWorker.test()

    except Exception as e:
        # Helps debugging in Celery logs
        self.retry(exc=e, countdown=5, max_retries=3)
