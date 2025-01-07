from django.db import models
from . import User
from .sound import Sound
from django.utils import timezone
from django.core.exceptions import ValidationError

class Category(models.TextChoices):
    MUSIC = 'MUSIC', 'Music'
    COMEDY = 'COMEDY', 'Comedy'
    EDUCATION = 'EDUCATION', 'Education'
    FITNESS = 'FITNESS', 'Fitness'
    FOOD = 'FOOD', 'Food'
    TRAVEL = 'TRAVEL', 'Travel'
    OTHER = 'OTHER', 'Other'

class Video(models.Model):
    description = models.CharField(max_length=255)
    creator = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    sound = models.ForeignKey(Sound, related_name='videos', blank=True, null=True, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)
    
    private = models.BooleanField(default=False)
    
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description}"


class HashTag(models.Model):
    tag = models.CharField(max_length=15, null=False, blank=False)
    video = models.ForeignKey(Video, related_name='hashtags', on_delete=models.CASCADE)

    def __str__(self):
        return self.tag

def validate_progress(value):
    if value < 0 or value > 100:
        raise ValidationError('Progress must be between 0 and 100.')
    
class View(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, related_name='views', blank=False, null=False, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0, validators=[validate_progress])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user.id} viewed Video {self.video.id} with progress {self.progress}%"
    
    def on_view(video_id, user, progress):
        video = Video.objects.filter(id=video_id).first()

        if not video:
            return ValidationError("Video Not Exist")
    
        view_instance = View.objects.filter(video=video, user=user).first()

        if progress > 80:
            for hashtag in video.hashtags.all():
                Recomended.on_create(user=user, hashtag=hashtag, category=video.category)

        if view_instance:
            view_instance.progress = progress
            view_instance.save()
            return f"Video View Updated to {progress}"
        else:
            View.objects.create(video=video, user=user, progress=progress)
            return f"Video View New {progress}"


class Like(models.Model):
    user = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, related_name='likes', blank=False, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.video.description} liked by: {self.user.firstname}"
    
    @staticmethod
    def on_like(user, video_id):
        video = Video.objects.filter(id=video_id).first()

        if not video:
            return ValidationError("Video Not Exist")
        
        like_instance = Like.objects.filter(user=user, video=video).first()
        if like_instance:
            like_instance.delete()
            return "Unlike successful"
        else:
            Like.objects.create(user=user, video=video)
            for hashtag in video.hashtags.all():
                Recomended.on_create(user, hashtag, video.category)
            return "Like successful"
        

class Recomended(models.Model):
    user = models.ForeignKey(User, related_name="recomended_user", on_delete=models.CASCADE)
    
    hashtag = models.ForeignKey(HashTag,related_name="recomended_hashtag", on_delete=models.CASCADE)
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)


    @staticmethod
    def on_create(user, hashtag, category):
        list_of_recomendeds = Recomended.objects.filter(hashtag=hashtag, user=user)

        if list_of_recomendeds.exists():
            list_of_recomendeds.update(category=category, created_at=timezone.now())
            return list_of_recomendeds.first() 
        else:
            return Recomended.objects.create(hashtag=hashtag, user=user, category=category)
    
    def __str__(self):
        return f"{self.user.firstname} | {self.hashtag.tag} | {self.category}"

