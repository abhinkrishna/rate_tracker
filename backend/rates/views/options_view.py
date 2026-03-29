from rate_tracker.view import CustomAPIView
from rates.models import Provider, RateType, Currency
from rates.serializers import ProviderSerializer, RateTypeSerializer, CurrencySerializer


class AvailableOptionsAPIView(CustomAPIView):
    """
    Returns available providers, rate types and currencies.
    """

    def get(self, request):
        cache_key = "rates_available_options"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return self.OK.to_response(data=cached_data)

        providers = Provider.objects.all().order_by("name")
        rate_types = RateType.objects.all().order_by("name")
        currencies = Currency.objects.all().order_by("code")

        data = {
            "providers": ProviderSerializer(providers, many=True).data,
            "rate_types": RateTypeSerializer(rate_types, many=True).data,
            "currencies": CurrencySerializer(currencies, many=True).data,
        }

        # Cache for 1 hour
        self.cache.set(cache_key, data, timeout=3600)

        return self.OK.to_response(data=data)
