from rest_framework import serializers
from ..models import Video, HashTag, Like, View, Category
from .user import ProfileSerializer
from .sound import SoundSerializer

class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ['tag']


class VideoSerializer(serializers.ModelSerializer):
    hashtags = HashTagSerializer(many=True)
    likes = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    creator = ProfileSerializer()
    sound = SoundSerializer()
    
    class Meta:
        model = Video
        fields = ['id', 'url', 'sound', 'likes', 'private', 'views', 'created_at', 'description', 'creator', 'hashtags']

    def get_likes(self, obj):
        return Like.objects.filter(video=obj).count()

    def get_views(self, obj):
        return View.objects.filter(video=obj).count()
    
class CreateVideoSerializer(serializers.Serializer):
    video = serializers.FileField(write_only=True)
    hashtags = HashTagSerializer(many=True)
    description = serializers.CharField(write_only=True)
    soundId = serializers.CharField(required=False, allow_blank=True)
    private = serializers.BooleanField()
    category = serializers.ChoiceField(
        choices=Category.choices, 
        required=False, 
        allow_blank=True
    )

    def validate(self, attrs):
        if not attrs.get('category'):
            attrs['category'] = Category.OTHER
        return attrs