from django.db import models
from . import User
from ..utils import file_upload, validate_file


def upload_sound(instance, filename):
    return file_upload(instance, filename, 'sounds/')

class Sound(models.Model):
    url = models.FileField(upload_to=upload_sound, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    creator = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.name and self.creator:
            self.name = f"{self.creator.firstname} {self.creator.lastname} sound"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"
    
    def clean(self):
        if self.url:
            validate_file(self.url, 'mp3')
