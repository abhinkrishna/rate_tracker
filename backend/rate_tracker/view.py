from rate_tracker.response import SUCCESS_RESPONSE, ERROR_RESPONSE
from rest_framework.views import APIView
from datetime import date, datetime


class CustomAPIView(APIView, SUCCESS_RESPONSE, ERROR_RESPONSE):
    date = None
    timestamp = None

    def initial(self, request, *args, **kwargs):
        self.date = date.today()
        self.timestamp = datetime.now()
        super().initial(request, *args, **kwargs)

    def log(self, request):
        # log the request with celery to take the load from
        # django to celery and add log entry to a log database
        pass


class HealthCheckAPIView(CustomAPIView):
    def get(self, request):
        response = {"status": "healthy", "timestamp": self.timestamp}
        return self.OK.to_response(response)
