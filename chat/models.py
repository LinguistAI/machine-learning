import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ChatBot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    profile_image = models.TextField()
    prompt = models.TextField()
    voice_characteristics = models.TextField()
    difficulty_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    def __str__(self):
        return "ChatBot: " + self.name

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user_email = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    bot = models.ForeignKey(ChatBot, on_delete=models.CASCADE, related_name='conversations')
    
    def __str__(self):
        return f"Conversation: {self.title}"    
    

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_email = models.CharField(max_length=255)
    sender_type = models.CharField(max_length=10)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    message_text = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    def __str__(self):
        return f"{self.sender_type}: {self.message_text}"
    

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