

from rest_framework import serializers

from mcq.models import MCTQuestion, MCTTest

class MCTQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCTQuestion
        fields = '__all__'

class MCTTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCTTest
        fields = '__all__'
        
        