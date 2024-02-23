from django.db import models

class Profile(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    likes = models.TextField(null=True)
    loves = models.TextField(null=True)
    dislikes = models.TextField(null=True)
    hates = models.TextField(null=True)
    profile_info = models.TextField(null=True)
    email = models.CharField(max_length=255, unique=True)
    