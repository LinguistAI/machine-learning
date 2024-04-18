import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from chat.models import UnknownWord
# Create your models here.

class WordScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    word = models.CharField(max_length=255)
    gramatical_correctness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    spelling = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    punctuation = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    capitalization = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    word_choice = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    sentence_structure = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rest_of_sentence = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    reasoning = models.TextField()
    unknownWord = models.ForeignKey(UnknownWord, on_delete=models.CASCADE, related_name='wordScores')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.word