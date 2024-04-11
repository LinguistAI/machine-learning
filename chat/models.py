import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UnknownWord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)
    word = models.CharField(max_length=255)
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='unknownWords', null=True)
    isActive = models.BooleanField(default=True)
    confidenceLevel = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    def __str__(self):
        return "UnknownWord: " + self.word

class ChatBot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    profileImage = models.TextField()
    prompt = models.TextField()
    voiceCharacteristics = models.TextField()
    difficultyLevel = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    def __str__(self):
        return "ChatBot: " + self.name

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)
    userEmail = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    bot = models.ForeignKey(ChatBot, on_delete=models.CASCADE, related_name='conversations')
    unknownWords = models.ManyToManyField(UnknownWord, related_name='conversations')
    
    def __str__(self):
        return f"Conversation: {self.title}"    
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    senderEmail = models.CharField(max_length=255)
    senderType = models.CharField(max_length=10)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)
    messageText = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    def __str__(self):
        return f"{self.senderType}: {self.messageText}"
