from django.contrib import admin
from .models import Provider, Currency, RateType, IngestRaw, Rate


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "symbol", "country")
    search_fields = ("code", "name", "country")


@admin.register(RateType)
class RateTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(IngestRaw)
class IngestRawAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "status", "response_id", "created_at", "updated_at")
    list_filter = ("status", "source", "created_at")
    search_fields = ("source", "response_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "provider",
        "currency",
        "rate_type",
        "rate_value",
        "effective_date",
        "ingestion_ts",
    )
    list_filter = ("provider", "currency", "rate_type", "effective_date")
    search_fields = ("raw_response_id", "source_url")
    date_hierarchy = "effective_date"
