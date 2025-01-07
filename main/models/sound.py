from django.db import models
from . import User


class Sound(models.Model):
    url = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    creator = models.ForeignKey(User, blank=False, null=False, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.name and self.creator:
            self.name = f"{self.creator.firstname} {self.creator.lastname} sound"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"