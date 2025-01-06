from . import User
from django.db import models

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_valid(self):
         return f"{self.user.email} - {self.session_token}"
    
    def __str__(self):
         return f"{self.user.firstname} | {self.created_at} / {self.expires_at}"