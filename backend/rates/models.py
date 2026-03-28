from django.db import models
from rate_tracker.constants import IngestRawStatus


class Provider(models.Model):
    name = models.CharField(max_length=255, unique=True)
    aliases = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Provider"
        verbose_name_plural = "Providers"


class Currency(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"


class RateType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    aliases = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rate Type"
        verbose_name_plural = "Rate Types"


class IngestRaw(models.Model):
    source = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=IngestRawStatus.choices,
        default=IngestRawStatus.PENDING
    )
    response_id = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source} - {self.response_id} ({self.status})"

    class Meta:
        verbose_name = "Ingest Raw"
        verbose_name_plural = "Ingest Raw Data"


class Rate(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="rates")
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="rates")
    rate_type = models.ForeignKey(RateType, on_delete=models.CASCADE, related_name="rates")
    rate_value = models.DecimalField(max_digits=20, decimal_places=10)
    effective_date = models.DateField()
    ingestion_ts = models.DateTimeField()
    source_url = models.URLField(max_length=500, blank=True, null=True)
    raw_response_id = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.currency.code} - {self.rate_value} ({self.provider.name})"

    class Meta:
        verbose_name = "Rate"
        verbose_name_plural = "Rates"
        indexes = [
            models.Index(fields=['effective_date', 'currency', 'provider']),
        ]
