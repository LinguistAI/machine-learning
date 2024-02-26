

from chat.models import ChatBot, Conversation, Message
from rest_framework import serializers
        
        
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

    class Meta:
        model = Conversation
        fields = '__all__'