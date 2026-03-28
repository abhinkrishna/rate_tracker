from rate_tracker.view import CustomAPIView


class HistoryRateAPIView(CustomAPIView):
    def get(self, request):
        return self.OK.to_response()
