from analytics.models import APIRequestLog

class LogAPIRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith('/api/'):
            APIRequestLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
            )
        return response
