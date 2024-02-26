

from chat.models import ChatBot, Conversation, Message
from rest_framework import serializers


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'
        
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        

class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = ['id', 'createdDate', 'updatedDate', 'name', 'description', 'profileImage', 'voiceCharacteristics', 'difficultyLevel']
        