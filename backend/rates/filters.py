import django_filters
from rates.models import Rate

class LatestRateFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(field_name="rate_type__name", lookup_expr="iexact")

    class Meta:
        model = Rate
        fields = ["type"]


class HistoryRateFilter(django_filters.FilterSet):
    provider = django_filters.CharFilter(field_name="provider__name", lookup_expr="iexact", required=True)
    type = django_filters.CharFilter(field_name="rate_type__name", lookup_expr="iexact", required=True)
    from_date = django_filters.DateFilter(field_name="effective_date", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="effective_date", lookup_expr="lte")

    class Meta:
        model = Rate
        fields = ["provider", "type", "from_date", "to_date"]
