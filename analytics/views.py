from rest_framework.views import APIView
from rest_framework.response import Response
from analytics.models import APIRequestLog
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class APIAnalyticsView(APIView):
    @swagger_auto_schema(
        operation_summary="Get API Analytics",
        operation_description="Returns the number of requests to each endpoint, with the ability to filter by user and method.",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="User ID for filtering requests",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'method',
                openapi.IN_QUERY,
                description="HTTP Method (GET, POST, PUT, DELETE и т.д.)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: "Analytics data"}
    )
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        method = request.query_params.get('method')

        logs = APIRequestLog.objects.all()

        if user_id:
            logs = logs.filter(user_id=user_id)
        if method:
            logs = logs.filter(method=method.upper())

        analytics = logs.values('endpoint').annotate(
            request_count=Count('id')
        ).order_by('-request_count')

        return Response(analytics)
