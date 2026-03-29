from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rate_tracker.view import CustomAPIView
from rates.serializers import IngestRawSerializer
from rates.models import Rate, Provider, Currency, RateType
from rates.utils.ingestion_worker import IngestionWorker
from django.utils import timezone


class RateIngestHookAPIView(CustomAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _resolve_model(self, model_class, raw_value, is_currency=False):
        alias = IngestionWorker._normalize_alias(raw_value)
        
        # Search existing
        for obj in model_class.objects.all():
            compare_field = obj.code if is_currency else obj.name
            if alias in obj.aliases or IngestionWorker._normalize_alias(compare_field) == alias:
                if alias not in obj.aliases:
                    obj.aliases.append(alias)
                    obj.save(update_fields=["aliases"])
                return obj
                
        # Create new
        if is_currency:
            obj, created = model_class.objects.get_or_create(
                code=raw_value[:10], defaults={"name": raw_value}
            )
        else:
            obj, created = model_class.objects.get_or_create(name=raw_value)
            
        if created:
            obj.aliases = [alias]
            obj.save(update_fields=["aliases"])
        elif alias not in obj.aliases:
            obj.aliases.append(alias)
            obj.save(update_fields=["aliases"])
            
        return obj

    def post(self, request):
        serializer = IngestRawSerializer(data=request.data)
        if not serializer.is_valid():
            return self.BAD_REQUEST.to_response(
                message="Validation failed", data=serializer.errors
            )

        validated_data = serializer.validated_data

        try:
            # Get or create related models using alias caching system
            provider = self._resolve_model(Provider, validated_data["provider_name"])
            currency = self._resolve_model(
                Currency, validated_data["currency_code"], is_currency=True
            )
            rate_type = self._resolve_model(RateType, validated_data["rate_type_name"])

            # Use update_or_create or just save
            # The ingestion pipeline uses response_id for idempotency on raw ingest
            # For Rate, raw_response_id is unique
            rate, created = Rate.objects.update_or_create(
                raw_response_id=validated_data["raw_response_id"],
                defaults={
                    "provider": provider,
                    "currency": currency,
                    "rate_type": rate_type,
                    "rate_value": validated_data["rate_value"],
                    "effective_date": validated_data["effective_date"],
                    "source_url": validated_data.get("source_url", ""),
                    "ingestion_ts": timezone.now(),
                },
            )

            # Invalidate cache
            self.cache.delete("rates_latest")
            self.cache.delete(f"rates_latest_{rate_type.name}")
            self.cache.delete("rates_available_options")
            self.cache.delete_pattern("rates_history_*")

            if created:
                return self.CREATED.to_response(
                    message="Rate ingested successfully."
                    if created
                    else "Rate updated successfully.",
                    data={"id": rate.id, "raw_response_id": rate.raw_response_id},
                )
            else:
                return self.BAD_REQUEST.to_response(
                    message="Rate already exists.",
                    data={"id": rate.id, "raw_response_id": rate.raw_response_id},
                )

        except Exception as e:
            # Return a 422 or 400 for errors instead of 500s
            return self.UNPROCESSABLE_ENTITY.to_response(message=str(e))
