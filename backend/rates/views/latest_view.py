from rate_tracker.view import CustomAPIView
from rates.models import Rate
from rates.serializers import RateSerializer

from rates.filters import LatestRateFilter

class LatestRateAPIView(CustomAPIView):
    def get(self, request):
        rate_type = request.query_params.get("type")
        cache_key = "rates_latest"
        if rate_type:
            cache_key += f"_{rate_type}"

        cached_data = self.cache.get(cache_key)
        if cached_data:
            return self.OK.to_response(data=cached_data)

        queryset = Rate.objects.select_related("provider", "currency", "rate_type").order_by(
            "provider_id", "-effective_date", "-ingestion_ts"
        )
        
        filterset = LatestRateFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return self.BAD_REQUEST.to_response(message="Invalid filters applied", data=filterset.errors)
        
        queryset = filterset.qs
        # DISTINCT ON provider_id guarantees one rate per provider
        queryset = queryset.distinct("provider_id")

        serializer = RateSerializer(queryset, many=True)
        data = serializer.data
        
        # Cache for 15 minutes, invalidate upon ingest
        self.cache.set(cache_key, data, timeout=60 * 15)

        return self.OK.to_response(data=data)
