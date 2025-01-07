from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Video, HashTag, Like, Recomended, View, Sound
from ..serializers.video import CreateVideoSerializer, VideoSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max
from rest_framework.exceptions import NotFound

class CreateVideoView(generics.GenericAPIView):
    serializer_class = CreateVideoSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        soundId = serializer.validated_data.get('soundId', None)
        url = serializer.validated_data.get('url')
        description = serializer.validated_data.get("description")
        hashtags = serializer.validated_data.get("hashtags")
        category = serializer.validated_data.get("category") 
        private = serializer.validated_data.get("private")

        user = request.user

        if soundId:
            sound = Sound.objects.filter(id=soundId).first()

            if not sound:
                raise NotFound(detail="Sound not found.") 
            
            video = Video.objects.create(url=url, creator=user, description=description, category=category, private=private, sound=sound)
        else:
            video = Video.objects.create(url=url, creator=user, description=description, category=category, private=private)

        hashtag_objects = [
            HashTag(video=video, tag=f"#{hash_data.get("tag")}") for hash_data in hashtags
        ]
        HashTag.objects.bulk_create(hashtag_objects)

        return Response(VideoSerializer(video).data)
    

class LikeVideoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        user = request.user

        like = Like.on_like(user=user, video_id=id)
        
        return Response(like)
    
class ViewVideo(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, progress, *args, **kwargs):
        user = request.user

        view = View.on_view(video_id=id, user=user, progress=progress)
        
        return Response(view)

class ListBySound(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, soundId, *args, **kwargs):
        user = request.user

        limit = int(request.query_params.get('limit', 10))
        
        sound = Sound.objects.filter(id=soundId).first()

        if not sound:
            raise NotFound(detail="Sound not found.") 
        
        videos = Video.objects.filter(sound=sound)\
            .exclude(creator=user, private=True)\
            .annotate(like_count=Count('likes'))\
            .order_by('-like_count')[:limit]
        
        serialized_videos = VideoSerializer(videos, many=True).data
        return Response(serialized_videos)
    
class ForYouView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        limit = int(request.query_params.get('limit', 10))


        videos = Video.objects.all().exclude(private=False).order_by('-created_at')

        if user:
            recommended_hashtags = list(
                Recomended.objects.filter(user=user)
                .order_by('-created_at')
                .values_list('hashtag__tag', flat=True)[:15]
            )

            recommended_categories = list(
                Recomended.objects.filter(user=user)
                .order_by('-created_at')
                .values_list('category', flat=True)[:15]
            )

            if recommended_hashtags or recommended_categories:
                videos = (
                    Video.objects.exclude(creator=user)
                    .exclude(private=True)
                    .exclude(
                        views__user=user,
                        views__created_at__gte=timezone.now() - timedelta(days=2) 
                    )
                    .annotate(
                        hashtag_relevance=Count('hashtags', filter=Q(hashtags__tag__in=recommended_hashtags)),
                        category_relevance=Count('id', filter=Q(category__in=recommended_categories)),
                    )
                    .order_by('-hashtag_relevance', '-category_relevance', '-created_at')
                )
            else:
                videos = Video.objects.exclude(creator=user).exclude(private=True).order_by('-created_at')

        videos = videos[:limit]

        serialized_videos = VideoSerializer(videos, many=True).data
        return Response(serialized_videos)
    

class MyVideoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        limit = int(request.query_params.get('limit', 10))
        private = bool(request.query_params.get('private', False))
        
        videos =  Video.objects.filter(creator=user, private=private).order_by('-created_at')[:limit]
        
        serialized_videos = VideoSerializer(videos, many=True).data
        return Response(serialized_videos)
    

class LikedVideoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        limit = int(request.query_params.get('limit', 10))

        videos = (
            Video.objects.filter(likes__user=user, private=False)
            .annotate(last_liked_at=Max('likes__created_at'))
            .order_by('-last_liked_at')[:limit]
        )
        
        serialized_videos = VideoSerializer(videos, many=True).data
        return Response(serialized_videos)