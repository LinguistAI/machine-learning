from rest_framework import serializers

from chat.serializers import ConversationSerializer, UnknownWordSerializer
from mcq.models import MCTQuestion, MCTTest, Item, DoubleAnswerItem, EliminateItem


class MCTQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = MCTQuestion
        fields = ['id', 'email', 'question', 'options', 'answer', 'word', 'createdAt', 'updatedAt', 'hasUserAnswered',
                  'isUserCorrect', 'userAnswer', 'numTriesLeft']

    def get_options(self, obj: MCTQuestion):
        return [obj.option1, obj.option2, obj.option3, obj.option4]


class MCTQuestionHiddenAnswerSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = MCTQuestion
        fields = ['id', 'email', 'question', 'options', 'createdAt', 'updatedAt', 'hasUserAnswered', 'isUserCorrect',
                  'numTriesLeft']

    def get_options(self, obj: MCTQuestion):
        return [obj.option1, obj.option2, obj.option3, obj.option4]


class MCTTestHiddenAnswerSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    questions = MCTQuestionHiddenAnswerSerializer(many=True, read_only=True)
    unknownWords = UnknownWordSerializer(many=True, read_only=True)

    class Meta:
        model = MCTTest
        fields = '__all__'


class MCTTestSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    questions = MCTQuestionSerializer(many=True, read_only=True)
    unknownWords = UnknownWordSerializer(many=True, read_only=True)

    class Meta:
        model = MCTTest
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class DoubleAnswerItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubleAnswerItem
        fields = '__all__'


class EliminateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EliminateItem
        fields = '__all__'


def getItemSerializer(item):
    # Serialize the item based on its type
    if isinstance(item, DoubleAnswerItem):
        serializer = DoubleAnswerItemSerializer(item)
    elif isinstance(item, EliminateItem):
        serializer = EliminateItemSerializer(item)
    else:
        serializer = ItemSerializer(item)
    return serializer
