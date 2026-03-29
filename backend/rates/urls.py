from django.urls import path
from rates.views.latest_view import LatestRateAPIView
from rates.views.history_view import HistoryRateAPIView
from rates.views.ingest_hook_view import RateIngestHookAPIView
from rates.views.options_view import AvailableOptionsAPIView

urlpatterns = [
    path("latest", LatestRateAPIView.as_view(), name="rates-latest"),
    path("history", HistoryRateAPIView.as_view(), name="rates-history"),
    path("ingest/", RateIngestHookAPIView.as_view(), name="rates-ingest"),
    path("options", AvailableOptionsAPIView.as_view(), name="rates-options"),
]
