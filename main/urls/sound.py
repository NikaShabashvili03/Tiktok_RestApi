from django.urls import path
from main.views.sound import CreateSoundView, ListSoundView, SoundById

urlpatterns = [
    path('create', CreateSoundView.as_view(), name='create'),
    path('list', ListSoundView.as_view(), name='list-sounds'),
    path('one/<int:id>', SoundById.as_view(), name='sound-by-id')
]