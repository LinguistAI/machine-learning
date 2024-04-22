

from profiling.models import Profile
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['loves', 'likes', 'dislikes', 'hates', 'id', 'createdDate', 'updatedDate']
        