from datetime import timedelta, date

from rest_framework.decorators import api_view
from chat.models import Message
from constants.header_constants import HEADER_USER_EMAIL
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count
from django.db.models import F


@swagger_auto_schema(
    method='get',
    operation_description="Get total message counts sent to each bot",
    operation_id="GetMessageCountAggregate",
    operation_summary="Get total message counts sent to each bot",
    manual_parameters=[
        openapi.Parameter(
            name="sort",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="The sorting order for the message counts. Allowed values: 'asc' or 'desc'. Default is 'desc'."
        ),
        openapi.Parameter(
            name="daysLimit",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Number of days to limit the data to, e.g., the last 30 days"
        )
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
def get_message_count_aggregate(request):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    email = request.headers.get(HEADER_USER_EMAIL)
    if not email:
        return generate_error_response(400, "Authentication is required")

    # Get sorting order from URL parameter
    sorting_order = request.GET.get('sort', 'desc')  # Default to descending order

    # Get the value of num_days from the query parameters
    num_days = request.GET.get('daysLimit', None)
    if num_days is not None:
        try:
            num_days = int(num_days)
            start_date = date.today() - timedelta(days=num_days)
        except ValueError:
            return generate_error_response(400, "Invalid value for 'num_days'. Must be an integer.")
    else:
        start_date = None  # No date filtering

    # Query messages based on user
    aggregate_msg_count = Message.objects.filter(senderEmail=email)

    # Apply date filtering if start_date is provided
    if start_date:
        aggregate_msg_count = aggregate_msg_count.filter(createdDate__date__gte=start_date)

    aggregate_msg_count = aggregate_msg_count \
        .annotate(botId=F('conversation__bot__id')) \
        .values('botId') \
        .annotate(messageCountByBot=Count('id'))

    if sorting_order == 'asc':
        aggregate_msg_count = aggregate_msg_count.order_by('messageCountByBot')
    elif sorting_order == 'desc':
        aggregate_msg_count = aggregate_msg_count.order_by('-messageCountByBot')

    # If no messages are found, return an empty list
    if aggregate_msg_count is None:
        aggregate_msg_count = []

    return generate_success_response("Aggregate message counts:", aggregate_msg_count)
