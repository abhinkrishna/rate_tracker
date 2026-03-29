from rate_tracker.response import SUCCESS_RESPONSE, ERROR_RESPONSE
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from datetime import date, datetime

from rate_tracker.cache import CacheUtility


class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 1000


class CustomAPIView(APIView, SUCCESS_RESPONSE, ERROR_RESPONSE):
    date = None
    timestamp = None

    def initial(self, request, *args, **kwargs):
        self.date = date.today()
        self.timestamp = datetime.now()
        super().initial(request, *args, **kwargs)

    pagination_class = CustomPagination
    cache = CacheUtility()

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_data(self, data):
        if self.paginator is None:
            return data
        return {
            "count": self.paginator.page.paginator.count,
            "next": self.paginator.get_next_link(),
            "previous": self.paginator.get_previous_link(),
            "page_number": self.paginator.page.number,
            "page_size": self.paginator.page.paginator.per_page,
            "has_next": self.paginator.page.has_next(),
            "has_prev": self.paginator.page.has_previous(),
            "results": data,
        }


class HealthCheckAPIView(CustomAPIView):
    def get(self, request):
        response = {"status": "healthy", "timestamp": self.timestamp}
        return self.OK.to_response(response)
