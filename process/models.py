from django.db import models
from django.contrib.auth.models import User
from main.models import project
# Create your models here.

#intermedia stats for scoring while processing
# class stats(models.Model):
#     def __unicode__(self):
#         return self.name
    
#     name = models.CharField(max_length=50)
#     project = models.ForeignKey(project)
#     plate = models.CharField(max_length=50)
#     replicate = models.CharField(max_length=50)
#     value = models.FloatField()
