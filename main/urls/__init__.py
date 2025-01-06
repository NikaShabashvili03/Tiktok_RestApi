from django.urls import path, include

urlpatterns = [
    path('video/', include('main.urls.video')),
    path('user/', include('main.urls.user')),
]