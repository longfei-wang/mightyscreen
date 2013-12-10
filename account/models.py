from django.db import models
from django.contrib.auth.models import AbstractUser,User
# Create your models here.


class userprofile (models.Model):
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    