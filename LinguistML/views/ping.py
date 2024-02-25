from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utils.http_utils import generate_success_response

@swagger_auto_schema(
    method='get',
    operation_description="Ping the server",
    operation_id="Ping the server",
    operation_summary="Ping the server",
    responses={
        "200": openapi.Response(
            description="Server is up",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Server is up"
                }
            }
        )
    }
)
@api_view(['GET'])
def ping(request):
    return generate_success_response("Server is up", "Server is up")
