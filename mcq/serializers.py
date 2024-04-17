

from rest_framework import serializers

from chat.serializers import ConversationSerializer
from mcq.models import MCTQuestion, MCTTest

class MCTQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCTQuestion
        fields = '__all__'

class MCTTestSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    questions = MCTQuestionSerializer(many=True)
    class Meta:
        model = MCTTest
        fields = '__all__'
        
        