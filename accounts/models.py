from django.db import models
from django.contrib.auth.models import User
from userena.models import UserenaBaseProfile

# Create your models here.


class usersprofile (UserenaBaseProfile):
    def __unicode__(self):
        return self.user.username
    
    user = models.OneToOneField(User,related_name='user_profile')
    
    affiliation = models.CharField(max_length=100)
    position = models.CharField(max_length=50)





