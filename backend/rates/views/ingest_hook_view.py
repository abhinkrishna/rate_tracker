from rate_tracker.view import CustomAPIView


class RateIngestHookAPIView(CustomAPIView):
    def post(self, request):
        return self.OK.to_response()
