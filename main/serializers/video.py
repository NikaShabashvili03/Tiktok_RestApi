from rest_framework import serializers
from ..models import Video, HashTag, Like, View

class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ['tag']


class VideoSerializer(serializers.ModelSerializer):
    hashtags = HashTagSerializer(many=True)
    likes = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'category', 'likes', 'views', 'created_at', 'description', 'creator', 'hashtags']

    def get_likes(self, obj):
        return Like.objects.filter(video=obj).count()

    def get_views(self, obj):
        return View.objects.filter(video=obj).count()
    
class CreateVideoSerializer(serializers.Serializer):
    hashtags = HashTagSerializer(many=True)
    description = serializers.CharField(write_only=True)