

import json
from profiling.models import Profile
from rest_framework import serializers
from drf_yasg import openapi
from drf_yasg.utils import swagger_serializer_method


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    createdDate = serializers.DateTimeField()
    updatedDate = serializers.DateTimeField()
    # Parse likes, dislikes, loves, hates and profileInfo as JSON
    # Return as JSON
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    loves = serializers.SerializerMethodField()
    hates = serializers.SerializerMethodField()
    profileInfo = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['loves', 'likes', 'dislikes', 'hates', 'profileInfo', 'id', 'createdDate', 'updatedDate']
    
    def get_likes(self, obj: Profile) -> dict:
        return json.loads(obj.likes) if obj.likes else None

    def get_dislikes(self, obj: Profile) -> dict:
        return json.loads(obj.dislikes) if obj.dislikes else None

    def get_loves(self, obj: Profile) -> dict:
        return json.loads(obj.loves) if obj.loves else None

    def get_hates(self, obj: Profile) -> dict:
        return json.loads(obj.hates) if obj.hates else None

    def get_profileInfo(self, obj: Profile) -> dict:
        return json.loads(obj.profileInfo) if obj.profileInfo else None