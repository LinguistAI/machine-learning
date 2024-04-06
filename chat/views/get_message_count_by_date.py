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
def get_message_count_by_date(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")

    # Get the parameters
    bot_id = request.GET.get('botId', None)
    sorting_order = request.GET.get('sort', DESCENDING_ORDER)
    days_limit = request.GET.get('daysLimit', None)

    # Parameter checks
    if bot_id is not None:
        try:
            # Check if the bot ID is a valid UUID
            uuid_obj = uuid.UUID(bot_id)
        except ValueError:
            return generate_error_response(400, "Invalid Bot ID")
        # Check if the bot exists
        if not ChatBot.objects.filter(id=uuid_obj).exists():
            return generate_error_response(404, "Bot not found")

    if days_limit is not None:
        try:
            days_limit = int(days_limit)
            start_date = date.today() - timedelta(days=days_limit)
        except ValueError:
            return generate_error_response(400, "Invalid value for 'daysLimit'. Must be an integer.")
    else:
        start_date = None  # No date filtering

    # Query messages
    msg_count = Message.objects.annotate(date=F('createdDate__date'), botId=F('conversation__bot__id')).filter(senderEmail=email)

    # Filter by optional parameters
    if bot_id is not None:
        msg_count = msg_count.filter(conversation__bot__id=bot_id)

    if start_date:
        msg_count = msg_count.filter(createdDate__date__gte=start_date)

    if sorting_order == ASCENDING_ORDER:
        msg_count = msg_count.order_by('date')
    else:
        msg_count = msg_count.order_by('-date')

    # Get message counts by date
    msg_count = msg_count.values('date').annotate(messageCount=Count('id'))

    # If no messages are found, return an empty list
    if not msg_count.exists():
        msg_count = []

    return generate_success_response("Message counts over time:", msg_count)
