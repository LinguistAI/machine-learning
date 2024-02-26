import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    

chatbot_output_example = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "created_date": "2021-08-30 14:00:00",
    "updated_date": "2021-08-30 14:00:00",
    "name": "Test Chatbot",
    "description": "This is a test chatbot",
    "profile_image": "test_image.png",
    "voice_characteristics": "British",
    "difficulty_level": 10,
}