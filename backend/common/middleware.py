import logging
import time
import traceback

from django.http import HttpRequest

logger = logging.getLogger("common.middleware")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        start = time.perf_counter()
        method = request.method
        path = request.get_full_path()
        ip = request.META.get("REMOTE_ADDR", "-")
        user = request.user if request.user.is_authenticated else None

        try:
            response = self.get_response(request)
        except Exception as exc:
            logger.error(
                "Unhandled exception on %s %s\n%s",
                request.method,
                request.get_full_path(),
                "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            )
            raise

        duration = (time.perf_counter() - start) * 1000
        status = response.status_code

        if status >= 500:
            logger.error(
                "%s %s %d %.0fms [%s] user=%s",
                method,
                path,
                status,
                duration,
                ip,
                user,
            )
        elif status >= 400:
            logger.warning(
                "%s %s %d %.0fms [%s] user=%s",
                method,
                path,
                status,
                duration,
                ip,
                user,
            )
        else:
            logger.info(
                "%s %s %d %.0fms [%s] user=%s",
                method,
                path,
                status,
                duration,
                ip,
                user,
            )

        return response
