import hashlib
from rate_tracker.view import CustomAPIView
from rates.models import Rate
from rates.serializers import RateSerializer



from rates.filters import HistoryRateFilter

class HistoryRateAPIView(CustomAPIView):
    def get(self, request):
        query_string = request.META.get('QUERY_STRING', '')
        cache_key_hash = hashlib.md5(query_string.encode('utf-8')).hexdigest()
        cache_key = f"rates_history_{cache_key_hash}"

        cached_data = self.cache.get(cache_key)
        if cached_data:
            return self.OK.to_response(data=cached_data)

        queryset = Rate.objects.select_related("provider", "currency", "rate_type").order_by("-effective_date", "-ingestion_ts")

        # Map 'from' and 'to' query parameters to the expected 'from_date' and 'to_date' names in the filterset
        filter_data = request.query_params.copy()
        if "from" in filter_data:
            filter_data["from_date"] = filter_data.get("from")
        if "to" in filter_data:
            filter_data["to_date"] = filter_data.get("to")

        filterset = HistoryRateFilter(filter_data, queryset=queryset)
        if not filterset.is_valid():
            return self.BAD_REQUEST.to_response(message="Invalid filters applied", data=filterset.errors)

        queryset = filterset.qs

        # Pagination
        result_page = self.paginate_queryset(queryset)
        if result_page is not None:
            serializer = RateSerializer(result_page, many=True)
            data = self.get_paginated_data(serializer.data)
        else:
            serializer = RateSerializer(queryset, many=True)
            data = serializer.data

        self.cache.set(cache_key, data, timeout=60 * 15)
        return self.OK.to_response(data=data)
