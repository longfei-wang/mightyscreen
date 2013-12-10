from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class userprofile (models.Model):
    user = models.OneToOneField(User)
    firstname= models.CharField(max_length=20)
    lastname= models.CharField(max_length=20)
    email = models.EmailField()
    affiliation = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    