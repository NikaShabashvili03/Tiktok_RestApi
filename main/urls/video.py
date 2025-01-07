from django.urls import path
from main.views.video import CreateVideoView, LikeVideoView, ForYouView, ViewVideo, MyVideoView, LikedVideoView, ListBySound

urlpatterns = [
    path('create', CreateVideoView.as_view(), name='create'),
    path('like/<int:id>', LikeVideoView.as_view(), name='like'),
    path('view/<int:id>/<int:progress>', ViewVideo.as_view(), name='view'),
    path('foryou', ForYouView.as_view(), name='for-you'),
    path('my', MyVideoView.as_view(), name='my-video'),
    path('liked', LikedVideoView.as_view(), name='liked-video'),
    path('sound/<int:soundId>', ListBySound.as_view(), name='list-by-sounds')
]