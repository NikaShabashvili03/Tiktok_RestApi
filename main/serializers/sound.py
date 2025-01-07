from rest_framework import serializers
from .user import ProfileSerializer
from ..models import Video, Sound


class SoundSerializer(serializers.ModelSerializer):
    usages = serializers.SerializerMethodField()

    class Meta:
        model = Sound
        fields = ['id', 'usages', 'url', 'name']

    def get_usages(self, obj):
        return Video.objects.filter(sound=obj).count()

class CreateSoundSerializer(serializers.Serializer):
    url = serializers.CharField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)