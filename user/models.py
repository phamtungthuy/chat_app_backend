from django.db import models
from django.contrib.auth.models import User
from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from .utils import sendForgetPasswordEmail

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    verification_code = models.CharField(null=True, blank=True, max_length=128)
    bio = models.CharField(null=True, blank=True, max_length=512)
    avatar_url = models.CharField(null=True, blank=True, max_length=512)
    phone_number = models.CharField(null=True, blank=True, max_length=15)
    address = models.CharField(null=True, blank=True, max_length=100)
    online = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
    
    @receiver(reset_password_token_created)
    def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
        sendForgetPasswordEmail(reset_password_token)
