import uuid
from django.db import models

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    likes = models.TextField(null=True)
    loves = models.TextField(null=True)
    dislikes = models.TextField(null=True)
    hates = models.TextField(null=True)
    profile_info = models.TextField(null=True)
    email = models.CharField(max_length=255, unique=True)

    def __str__(self):
        
        output_format = ""
        
        if self.profile_info:
            output_format += f"Profile Info: {self.profile_info}\n"
            
        if self.likes:
            output_format += f"Likes: {self.likes}\n"
            
        if self.loves:
            output_format += f"Loves: {self.loves}\n"
            
        if self.dislikes:
            output_format += f"Dislikes: {self.dislikes}\n"
        
        if self.hates:
            output_format += f"Hates: {self.hates}"
        
        if output_format.strip() == "":
            output_format = "No profile information available"
            
        return output_format