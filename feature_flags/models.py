import uuid
from django.db import models

class FeatureCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Feature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    rollout_percentage = models.FloatField(default=0.0)
    user_controlled = models.BooleanField(default=False)
    category = models.ForeignKey(FeatureCategory, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
class UserFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    expiresAt = models.DateTimeField(null=True, blank=True)
    context = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.email} - {self.feature.name}"