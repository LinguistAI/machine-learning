from datetime import timedelta, date

from rest_framework.decorators import api_view
from chat.models import Message
from chat.tasks.get_message_count_aggregate import get_message_count_aggregate
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
            description="Message counts retrieved successfully",
            examples={
                "application/json": {
                    "timestamp": "2021-08-30 14:00:00",
                    "status": 200,
                    "msg": "Aggregate message counts:",
                    "data": [{
                                "botId": "some id",
                                "messageCountByBot": 4
                            },
                            {
                                "botId": "another id",
                                "messageCountByBot": 2
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
                }
            }
        )
    }
)
@api_view(['GET'])
def get_message_count_aggregate_by_email(request, user_email: str):
    # Check the request header for email
    if not request.headers or HEADER_USER_EMAIL not in request.headers:
        return generate_error_response(400, "Authentication is required")

    logged_in_email = request.headers.get(HEADER_USER_EMAIL)
    if not logged_in_email:
        return generate_error_response(400, "Authentication is required")
    
    # Get sorting order from URL parameter
    sorting_order = request.GET.get('sort', 'desc')  # Default to descending order

    # Get the value of days_limit from the query parameters
    days_limit = request.GET.get('daysLimit', None)
    
    aggregate_msg_count = get_message_count_aggregate(user_email, sorting_order, days_limit)
    
    return generate_success_response("Aggregate message counts:", aggregate_msg_count)
