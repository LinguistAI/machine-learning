from LinguistML.views.Authentication import IsAuthenticatedByHeader
from LinguistML.views.DefaultPagination import DefaultPagination
from chat.models import Conversation, Message
from chat.serializers import MessageSerializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework import serializers
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class MessageListView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedByHeader]
    pagination_class = DefaultPagination

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')

        # Fetch the specified conversation
        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Build the queryset for messages
        queryset = Message.objects.filter(
            conversation=conversation).order_by('-createdDate')

        return queryset
