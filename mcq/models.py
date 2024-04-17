import uuid
from django.db import models
import random

class MCTQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255)
    question = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    word = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    hasUserAnswered = models.BooleanField(default=False)
    isUserCorrect = models.BooleanField(default=False)

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
    
class MCTTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255)
    conversation = models.ForeignKey('chat.Conversation', on_delete=models.CASCADE)
    questions = models.ManyToManyField(MCTQuestion)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isCompleted = models.BooleanField(default=False)
    correctPercentage = models.FloatField(default=0.0)

    def __str__(self):
        return "MCQ Test: " + self.email