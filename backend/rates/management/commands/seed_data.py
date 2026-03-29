from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from rates.models import Currency
from rates.tasks import ingest_task, validation_task, organizer_task
from celery import chain
import os


class Command(BaseCommand):
    help = "Seeds historical data via Celery chain: Ingest -> Validate -> Organize -> Cleanup"

    def create_superuser(self):
        User = get_user_model()

        su_username = os.getenv("DJANGO_SUPERUSER_USERNAME", "root")
        su_email = os.getenv("DJANGO_SUPERUSER_EMAIL", "root@example.com")
        su_password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "root")

        if not User.objects.filter(username=su_username).exists():
            User.objects.create_superuser(
                username=su_username, email=su_email, password=su_password
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{su_username}' created."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{su_username}' already exists.")
            )

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, "data", "rates_seed.parquet")
        self.create_superuser()

        source_data = {
            "name": "Sample rates seed data",
            "type": "parquet",
            "source": file_path,
            "creds": {},
        }

        self.stdout.write(
            self.style.SUCCESS(f"Preparing to seed data from {file_path}")
        )

        Currency.objects.update_or_create(
            code="USD",
            defaults={
                "name": "US Dollar",
                "aliases": ["us_dollar", "usd", "$"],
                "country": "United States",
                "symbol": "$",
            },
        )

        # 1. Trigger the asynchronous execution via Celery chain
        pipeline = chain(
            ingest_task.s(source_data), validation_task.si(), organizer_task.si()
        )
        result = pipeline.apply_async()

        self.stdout.write(self.style.SUCCESS("Asynchronous pipeline triggered!"))
        self.stdout.write(self.style.SUCCESS(f"Chain Root ID: {result.id}"))
        self.stdout.write("Check Celery logs for detailed execution progress.")
