from datetime import timedelta, date

from rest_framework.decorators import api_view
from chat.models import Message, ChatBot
from constants.header_constants import HEADER_USER_EMAIL
from constants.parameter_constants import ASCENDING_ORDER, DESCENDING_ORDER
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count
from django.db.models import F
import uuid
from chat.tasks.get_message_count_by_date import get_message_count_by_date

@swagger_auto_schema(
    method='get',
    operation_description="Get message counts sent over time, either to a bot or to all bots",
    operation_id="GetMessageCountOverTime",
    operation_summary="Get message counts sent over time, either to a bot or to all bots",
    manual_parameters=[
        openapi.Parameter(
            name='sort',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='Date sorting order for the results (asc or desc), default is descending',
            required=False
        ),
        openapi.Parameter(
            name='daysLimit',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Number of days to limit the data to, e.g., the last 30 days',
            required=False
        ),
        openapi.Parameter(
            name='botId',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description='ID of the bot to filter messages by',
            required=False
        ),
    ],
    responses={
        "200": openapi.Response(
            description="Message counts retrieved successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Message counts over time:",
                    "data": [{
                                "date": "2024-02-28",
                                "messageCount": 1
                            },
                            {
                                "date": "2024-03-13",
                                "messageCount": 3
                            }
                    ]
                }
            }
        ),
        "400": openapi.Response(
            description="Bad request",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 400,
                    "msg": "Authentication is required"
                },
            }
        ),
        "404": openapi.Response(
            description="Bot with the given id is not found",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 404,
                    "msg": "Bot not found"
                },
            }
        )
    }
)
@api_view(['GET'])
def get_message_count_by_date_by_email(request, user_email: str):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    logged_in_email = request.headers.get(HEADER_USER_EMAIL)
    if not logged_in_email:
        return generate_error_response(400, "Authentication is required")

    # Get the parameters
    bot_id = request.GET.get('botId', None)
    sorting_order = request.GET.get('sort', DESCENDING_ORDER)
    days_limit = request.GET.get('daysLimit', None)

    msg_count = get_message_count_by_date(user_email, bot_id, sorting_order, days_limit)
    
    return generate_success_response("Message counts over time:", msg_count)
