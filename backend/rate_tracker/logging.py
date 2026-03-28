import time
import logging
import json

logger = logging.getLogger("api_logger")


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Request data
        request_body = self.get_request_body(request)

        response = self.get_response(request)

        duration = time.time() - start_time

        log_data = {
            "method": request.method,
            "path": request.get_full_path(),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "user": str(request.user) if request.user.is_authenticated else None,
            "ip": self.get_client_ip(request),
            "request_body": request_body,
        }

        logger.info(json.dumps(log_data))

        return response

    def get_request_body(self, request):
        try:
            if request.body:
                body = json.loads(request.body.decode("utf-8"))
                return self.mask_sensitive_data(body)
        except Exception:
            return None
        return None

    def mask_sensitive_data(self, data):
        SENSITIVE_FIELDS = {"password", "token", "access", "refresh"}

        if isinstance(data, dict):
            return {
                key: ("***" if key.lower() in SENSITIVE_FIELDS else value)
                for key, value in data.items()
            }
        return data

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")
