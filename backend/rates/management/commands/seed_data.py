from celery import chain
from rates.tasks import ingest_task, validation_task, organizer_task, cleanup_task
from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Seeds historical data via Celery chain: Ingest -> Validate -> Organize -> Cleanup"

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, "data", "rates_seed.parquet")

        source_data = {
            "name": "Sample rates seed data",
            "type": "parquet",
            "source": file_path,
            "creds": {},
        }

        self.stdout.write(
            self.style.SUCCESS(f"Preparing to seed data from {file_path}")
        )

        # 1. Define the Celery chain (sequential tasks)
        # s() means subtask / signature
        pipeline = chain(
            ingest_task.s(source_data),
            validation_task.s(),
            organizer_task.s(),
            cleanup_task.s(),
        )

        # 2. Trigger the asynchronous execution
        result = pipeline.apply_async()

        self.stdout.write(self.style.SUCCESS(f"Asynchronous pipeline triggered!"))
        self.stdout.write(self.style.SUCCESS(f"Chain Root ID: {result.id}"))
        self.stdout.write("Check Celery logs for detailed execution progress.")
