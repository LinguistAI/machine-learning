

from chat.models import ChatBot, Conversation, Message, UnknownWord
from rest_framework import serializers
from drf_yasg import openapi

class UnknownWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnknownWord
        fields = '__all__'
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "Unknown Word",
            "properties": {
                "id": openapi.Schema(
                    title="ID",
                    type=openapi.TYPE_STRING,
                    example="d4b6b3b0-0b3b-4b3b-8b3b-0b3b4b3b4b3b",
                ),
                "listId": openapi.Schema(
                    title="List ID",
                    type=openapi.TYPE_STRING,
                    example="d4b6b3b0-0b3b-4b3b-8b3b-0b3b4b3b4b3b",
                ),
                "email": openapi.Schema(
                    title="Email",
                    type=openapi.TYPE_STRING,
                    example="email@email.com",
                ),
                "word": openapi.Schema(
                    title="Word",
                    type=openapi.TYPE_STRING,
                    example="linguist",
                ),
                "createdDate": openapi.Schema(
                    title="Created Date",
                    type=openapi.TYPE_STRING,
                    example="2021-08-30 14:00:00",
                ),
                "updatedDate": openapi.Schema(
                    title="Updated Date",
                    type=openapi.TYPE_STRING,
                    example="2021-08-30 14:00:00",
                ),
                "isActive": openapi.Schema(
                    title="Is Active",
                    type=openapi.TYPE_BOOLEAN,
                    example=True,
                ),
                "confidenceLevel": openapi.Schema(
                    title="Confidence Level",
                    type=openapi.TYPE_NUMBER,
                    example=23.2,
                ),
            }
        }
        
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        

class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = ['id', 'createdDate', 'updatedDate', 'name', 'description', 'profileImage', 'voiceCharacteristics', 'difficultyLevel']
        

class ConversationSerializer(serializers.ModelSerializer):
    bot = ChatBotSerializer(read_only=True)  # Use the ChatBotSerializer for the 'bot' field
    unknownWords = UnknownWordSerializer(many=True, read_only=True)  # Use the UnknownWordSerializer for the 'unknownWords' field

    class Meta:
        model = Conversation
        fields = ['id', 'createdDate', 'updatedDate', 'userEmail', 'bot', 'title', 'unknownWords']
        
