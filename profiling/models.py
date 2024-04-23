import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Hobby(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)
    likes = models.TextField(null=True)
    loves = models.TextField(null=True)
    dislikes = models.TextField(null=True)
    hates = models.TextField(null=True)
    profileInfo = models.TextField(null=True)
    email = models.CharField(max_length=255, unique=True)
    birthDate = models.DateField(null=True)
    hobbies = models.ManyToManyField(Hobby, related_name='profiles')
    name = models.CharField(max_length=255, null=True)
    # English level is an enum
    # DONT_KNOW - Don't know
    # BEGINNER - Beginner
    # INTERMEDIATE - Intermediate
    # ADVANCED - Advanced
    # NATIVE - Native
    
    class EnglishLevel(models.TextChoices):
        DONT_KNOW = 'DONT_KNOW', 'Don\'t know'
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'
        NATIVE = 'NATIVE', 'Native'
        
    englishLevel = models.CharField(
        max_length=255,
        choices=EnglishLevel.choices,
        default=EnglishLevel.DONT_KNOW,
    )

    def __str__(self):
        
        output_format = ""
        
        if self.profileInfo:
            output_format += f"Profile Info: {self.profileInfo}\n"
            
        if self.likes:
            output_format += f"Likes: {self.likes}\n"
            
        if self.loves:
            output_format += f"Loves: {self.loves}\n"
            
        if self.dislikes:
            output_format += f"Dislikes: {self.dislikes}\n"
        
        if self.hates:
            output_format += f"Hates: {self.hates}"
            
        if self.birthDate:
            output_format += f"Birth Date: {self.birthDate}\n"
        
        if self.englishLevel and self.englishLevel != self.EnglishLevel.DONT_KNOW:
            output_format += f"English Level: {self.englishLevel}\n"
        
        if self.hobbies:
            output_format += f"Hobbies: {', '.join([hobby.name for hobby in self.hobbies.all()])}\n"
            
        if self.name: 
            output_format += f"Name: {self.name}\n"
        
        if output_format.strip() == "":
            output_format = "No profile information available"
            
        return output_format