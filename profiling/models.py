import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.serializers.json import DjangoJSONEncoder

class JsonTextListField(models.TextField):
    def to_python(self, value):
        if isinstance(value, list):
            # Convert the list to a JSON string
            return DjangoJSONEncoder().encode(value)
        return value


class Hobby(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdDate = models.DateTimeField(auto_now_add=True)
    updatedDate = models.DateTimeField(auto_now=True)
    likes = JsonTextListField(null=True)
    loves = JsonTextListField(null=True)
    dislikes = JsonTextListField(null=True)
    hates = JsonTextListField(null=True)
    profileInfo = models.TextField(null=True)
    email = models.CharField(max_length=255, unique=True)
    birthDate = models.DateField(null=True)
    englishLevel = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    hobbies = models.ManyToManyField(Hobby, related_name='profiles')
    name = models.CharField(max_length=255, null=True)
    

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
        
        if self.englishLevel:
            output_format += f"English Level: {self.englishLevel}\n"
        
        if self.hobbies:
            output_format += f"Hobbies: {', '.join([hobby.name for hobby in self.hobbies.all()])}\n"
            
        if self.name: 
            output_format += f"Name: {self.name}\n"
        
        if output_format.strip() == "":
            output_format = "No profile information available"
            
        return output_format