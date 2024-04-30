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


def get_message_count_by_date(email, bot_id, sorting_order, days_limit):

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

    return msg_count
