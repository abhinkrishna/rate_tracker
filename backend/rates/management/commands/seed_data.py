from rates.tasks import ingest_data_smoke_test
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seeds the database with initial providers, rate types, and historical rate data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding data"))
        # start
        result = ingest_data_smoke_test.delay()
        self.stdout.write(
            self.style.SUCCESS(f"Celery has started the task, id: {result.id}")
        )
