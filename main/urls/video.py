from django.urls import path
from main.views.video import CreateVideoView, LikeVideoView, ForYouView, ViewVideo

urlpatterns = [
    path('create/', CreateVideoView.as_view(), name='create'),
    path('like/<int:id>', LikeVideoView.as_view(), name='like'),
    path('view/<int:id>/<int:progress>', ViewVideo.as_view(), name='view'),
    path('foryou', ForYouView.as_view(), name='for-you')
]