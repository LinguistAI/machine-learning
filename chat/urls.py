
from django.urls import path
from chat.views.MessageListView import MessageListView
from chat.views.clear_conversation import clear_conversation
from chat.views.create_conversation import create_conversation

from chat.views.delete_conversation import delete_conversation
from chat.views.delete_message import delete_message
from chat.views.generate_chat_response import generate_chat_response
from chat.views.get_conversation_by_id import get_user_conversation_by_id
from chat.views.get_conversation_messages import get_conversation_messages
from chat.views.get_last_conversation_messages import get_last_conversation_messages
from chat.views.get_all_conversation_messages import get_all_conversation_messages
from chat.views.get_user_conversations import get_user_conversations
from chat.views.bots.get_all_bots import get_all_bots
from chat.views.get_message_count_aggregate import get_message_count_aggregate
from chat.views.get_message_count_by_date import get_message_count_by_date

urlpatterns = [
    path('chat/send/<str:conversation_id>', generate_chat_response),
    path('chat/all/<str:conversation_id>', get_all_conversation_messages),
    path('chat/latest/<str:conversation_id>', get_last_conversation_messages),
    path('chat/messages/<str:conversation_id>', get_conversation_messages),
    path('chat/delete/<str:message_id>', delete_message),
    path('delete/<str:conversation_id>', delete_conversation),
    path('clear/<str:conversation_id>', clear_conversation),
    path('chat/count', get_message_count_by_date, name="get_message_count_by_date"),
    path('chat/count/aggregate', get_message_count_aggregate, name="get_message_count_aggregate"),
    path("create", create_conversation, name="create_conversation"),
    path("user", get_user_conversations, name="get_user_conversations"),
    path("user/<str:conversation_id>", get_user_conversation_by_id, name="get_conversation_by_id"),
    path("bots", get_all_bots),
]
