

from rest_framework import serializers

from chat.serializers import ConversationSerializer
from mcq.models import MCTQuestion, MCTTest

class MCTQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    
    class Meta:
        model = MCTQuestion
        fields = ['id', 'email', 'question', 'options', 'answer', 'word', 'createdAt', 'updatedAt', 'hasUserAnswered', 'isUserCorrect']

    def get_options(self, obj: MCTQuestion):
        return [obj.option1, obj.option2, obj.option3, obj.option4]
    
class MCTQuestionHiddenAnswerSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = MCTQuestion
        fields = ['id', 'email', 'question', 'options', 'word', 'createdAt', 'updatedAt', 'hasUserAnswered', 'isUserCorrect']
        
    def get_options(self, obj: MCTQuestion):
        return [obj.option1, obj.option2, obj.option3, obj.option4]

class MCTTestHiddenAnswerSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    questions = MCTQuestionHiddenAnswerSerializer(many=True)
    class Meta:
        model = MCTTest
        fields = '__all__'

class MCTTestSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    questions = MCTQuestionSerializer(many=True)
    class Meta:
        model = MCTTest
        fields = '__all__'
        
        