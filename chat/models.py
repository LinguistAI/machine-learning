from django.db import models

class Conversation(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    user_email = models.CharField(max_length=255)

class Message(models.Model):
    sender_email = models.CharField(max_length=255)
    sender_type = models.CharField(max_length=10)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    message_text = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    
    def __str__(self):
        return f"{self.sender_type}: {self.message_text}"