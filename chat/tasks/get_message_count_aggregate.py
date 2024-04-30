from datetime import timedelta, date

from rest_framework.decorators import api_view
from chat.models import Message
from constants.header_constants import HEADER_USER_EMAIL
from utils.http_utils import generate_error_response, generate_success_response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count
from django.db.models import F

def get_message_count_aggregate(email, sorting_order, days_limit):
    
    if days_limit is not None:
        try:
            days_limit = int(days_limit)
            start_date = date.today() - timedelta(days=days_limit)
        except ValueError:
            return generate_error_response(400, "Invalid value for 'daysLimit'. Must be an integer.")
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
    
    return aggregate_msg_count
