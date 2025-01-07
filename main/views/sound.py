from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Sound, Video
from ..serializers.sound import CreateSoundSerializer, SoundSerializer
from rest_framework.response import Response
from django.db.models import Count
from rest_framework.exceptions import NotFound

class CreateSoundView(generics.GenericAPIView):
    serializer_class = CreateSoundSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        url = serializer.validated_data.get("url")
        name = serializer.validated_data.get("name")
        user = request.user

        sound = Sound.objects.create(creator=user, name=name, url=url)

        serialized_sound = SoundSerializer(sound).data

        return Response(serialized_sound)

class ListSoundView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        limit = int(request.query_params.get('limit', 10))
        
        sounds =  Sound.objects.all().annotate(videos_count=Count('videos')).order_by('-videos_count')[:limit][:limit]
        
        serialized_sounds = SoundSerializer(sounds, many=True).data
        return Response(serialized_sounds)
    
class SoundById(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        sound = Sound.objects.filter(id=id).first()

        if not sound:
            raise NotFound(detail="Sound not found.")
        
        serialized_sounds = SoundSerializer(sound).data
        return Response(serialized_sounds)