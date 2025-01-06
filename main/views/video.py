from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Video, HashTag, Like, Recomended, View
from ..serializers.video import CreateVideoSerializer, VideoSerializer
from django.utils import timezone
from datetime import timedelta

class CreateVideoView(generics.GenericAPIView):
    serializer_class = CreateVideoSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = serializer.validated_data.get("description")
        hashtags = serializer.validated_data.get("hashtags")
        user = request.user

        video = Video.objects.create(creator=user, description=description)

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

class ForYouView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        limit = int(request.query_params.get('limit', 10))


        videos = Video.objects.all().order_by('-created_at')

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
                videos = Video.objects.exclude(creator=user).order_by('-created_at')

        videos = videos[:limit]

        serialized_videos = VideoSerializer(videos, many=True).data
        return Response(serialized_videos)