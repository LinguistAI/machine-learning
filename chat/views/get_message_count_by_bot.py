from datetime import timedelta, date

from rest_framework.decorators import api_view
from chat.models import Message
from constants.header_constants import HEADER_USER_EMAIL
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count
from django.db.models import F
import uuid


@swagger_auto_schema(
    method='get',
    operation_description="Get message counts sent to a bot over time",
    operation_id="GetMessageCountAggregateByBot",
    operation_summary="Get message counts sent to a bot over time",
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
            description='ID of the bot to filter messages by (required)',
            required=True
        ),
    ],
    responses={
        "200": openapi.Response(
            description="Messages retrieved successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Messages retrieved successfully",
                    "data": []
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
                }
            }
        )
    }
)
@api_view(['GET'])
def get_message_count_by_bot(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")

    # Get the bot's ID from the request parameters
    bot_id = request.GET.get('botId', None)
    if bot_id is None:
        return generate_error_response(400, "Bot ID is required")

    # Check if the bot ID is a valid UUID
    try:
        uuid.UUID(bot_id)
    except ValueError:
        return generate_error_response(400, "Invalid Bot ID")

    # Get sorting order from URL parameter
    sorting_order = request.GET.get('sort', 'desc')

    # Get the value of num_days from the query parameters
    num_days = request.GET.get('daysLimit', None)
    if num_days is not None:
        try:
            num_days = int(num_days)
        except ValueError:
            return generate_error_response(400, "Invalid value for 'num_days'. Must be an integer.")

    # Calculate the start date based on num_days
    if num_days is not None:
        start_date = date.today() - timedelta(days=num_days)
    else:
        start_date = None  # No date filtering

    # Query messages based on user and bot
    msg_count = Message.objects.filter(senderEmail=email, conversation__bot__id=bot_id)
    if start_date:
        msg_count = msg_count.filter(createdDate__date__gte=start_date)

    msg_count = msg_count \
        .annotate(date=F('createdDate__date'), botId=F('conversation__bot__id')) \
        .values('date', 'botId') \
        .annotate(messageCount=Count('id'))

    if sorting_order == 'asc':
        msg_count = msg_count.order_by('date')
    elif sorting_order == 'desc':
        msg_count = msg_count.order_by('-date')

    # If no messages are found, return an empty list
    if msg_count is None:
        msg_count = []

    return generate_success_response("Message counts over time:", msg_count)
