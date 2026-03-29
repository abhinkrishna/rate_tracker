from rest_framework import serializers
from rates.models import Rate, Provider, Currency, RateType

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ["id", "name"]

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["id", "name", "code", "symbol", "country"]

class RateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateType
        fields = ["id", "name"]

class RateSerializer(serializers.ModelSerializer):
    provider = serializers.StringRelatedField()
    currency = serializers.StringRelatedField()
    rate_type = serializers.StringRelatedField()

    class Meta:
        model = Rate
        fields = [
            "id",
            "provider",
            "currency",
            "rate_type",
            "rate_value",
            "effective_date",
            "ingestion_ts",
            "source_url",
            "raw_response_id",
        ]

class IngestRawSerializer(serializers.Serializer):
    # This serializer validates the incoming webhook JSON body.
    # It must map to our data model. The requirements say:
    # "Accepts JSON matching your data model, validates strictly"
    provider_name = serializers.CharField(max_length=255)
    currency_code = serializers.CharField(max_length=10)
    rate_type_name = serializers.CharField(max_length=255)
    rate_value = serializers.DecimalField(max_digits=20, decimal_places=10)
    effective_date = serializers.DateField()
    source_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
    raw_response_id = serializers.CharField(max_length=255)

