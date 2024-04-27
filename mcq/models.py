import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
import random


class MCTQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    option1 = models.JSONField(default=list)  # TODO: Convert options into a table?? the order?
    option2 = models.JSONField(default=list)
    option3 = models.JSONField(default=list)
    option4 = models.JSONField(default=list)
    answer = models.CharField(max_length=255)
    word = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    hasUserAnswered = models.BooleanField(default=False)
    isUserCorrect = models.BooleanField(default=False)
    userAnswer = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    numTriesLeft = models.IntegerField(default=1)

    def __str__(self):
        return "MCQ Question: " + self.question

    def randomize_options(self):
        options = [self.option1, self.option2, self.option3, self.option4]
        random.shuffle(options)
        # Now assign the shuffled options back to the object
        self.option1 = options[0]
        self.option2 = options[1]
        self.option3 = options[2]
        self.option4 = options[3]
        return self

    def get_eliminated_options(self):
        eliminated_options = []
        for option_field in ['option1', 'option2', 'option3', 'option4']:
            option_data = getattr(self, option_field)
            if option_data.get('isEliminated', True):
                eliminated_options.append(option_data['label'])
        return eliminated_options

class MCTTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255)
    conversation = models.ForeignKey('chat.Conversation', on_delete=models.CASCADE)
    questions = models.ManyToManyField(MCTQuestion)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isCompleted = models.BooleanField(default=False)
    correctPercentage = models.FloatField(default=0.0)
    unknownWords = models.ManyToManyField('chat.UnknownWord', related_name='mcq_tests')
    startedAt = models.DateTimeField(blank=True, null=True)
    completedAt = models.DateTimeField(blank=True, null=True)
    elapsedSeconds = models.FloatField(default=0.0)
    
    def __str__(self):
        return "MCQ Test: " + self.email


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100)
    question = models.ForeignKey(MCTQuestion, on_delete=models.CASCADE, related_name='%(class)s_items')
    maxNumOfUses = models.IntegerField(default=1)
    usesSoFar = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def use(self):
        if self.usesSoFar >= self.maxNumOfUses:
            raise ValueError("The maximum number of uses has been reached for this item")

            # Increment the usesSoFar field
        self.usesSoFar += 1
        self.save()


class DoubleAnswerItem(Item):
    def use(self):
        super().use()
        question = self.question
        if question.numTriesLeft == 1:
            question.numTriesLeft = 2
        question.save()


class EliminateItem(Item):
    def use(self):
        super().use()

        # Get the associated MCTQuestion object
        question = self.question

        # Identify the correct answer
        correct_answer = question.answer

        # Get the options
        options = {
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4
        }

        # Remove the correct answer from the options
        correct_option = options.pop(correct_answer, None)

        # Randomly choose two options to eliminate
        eliminated_options = random.sample(options.keys(), min(len(options), 2))

        # Mark the isEliminated field to True for the chosen options
        for option in eliminated_options:
            options[option]['isEliminated'] = True

        # Save the updated options back to MCTQuestion
        for key, value in options.items():
            setattr(question, key, value)

        # Add the correct answer back with isEliminated=False
        if correct_option:
            setattr(question, correct_answer, correct_option)

        question.save()

ITEM_TYPE_MAPPING = {
    "Double Answer": DoubleAnswerItem,
    "Eliminate Wrong Answer": EliminateItem,
}