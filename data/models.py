from django.db import models
from django.contrib.auth.models import User
import uuid

#Create your models here.


class csv_file(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    create_date = models.DateTimeField(auto_now_add = True, blank = True)

    project = models.ForeignKey(project,null=True,blank=True)

    raw_csv_file = models.FileField(null=True,upload_to='CSV')

    cleaned_csv_file = models.FileField(null=True,blank=True,upload_to='CSV')


#Data object abstract for all screening raw data. Real table is in app:data
#Two ways of identify compound. FaciclityID? or Plate+Well
class data_base(models.Model):
    
    def __unicode__(self):
    
        return self.library+self.plate_well
        
    class Meta:

        abstract=True
    
    library = models.CharField(max_length=50,verbose_name='Library')

    plate_well = models.CharField(max_length=50)#using plate well as unique identifier, not good for more than one libraries

    plate = models.CharField(max_length=20)

    well = models.CharField(max_length=20)
    
    hit=models.PositiveSmallIntegerField(default=0,verbose_name='Hit')

    schoice = (
    ('B','bad well'),
    ('E','empty'),
    ('P','positive control'),
    ('N','negative control'),
    ('X','compound'),
    )
    
    welltype=models.CharField(max_length=1,choices=schoice,default='X')

    project = models.ForeignKey(project)
    
    create_date = models.DateTimeField(auto_now_add = True, blank = True)
    
    create_by = models.ForeignKey(User,null=True,blank=True)


class project(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	name = models.CharField(max_length=10,verbose_name='Project Name')

	memo = models.TextField(blank=True)

	user = models.ForeignKey(User,null=True,blank=True)

	session = models.CharField(max_length=50,verbose_name='Session Key',blank=True)

	meta = models.TextField(blank=True)#this stores a dictionary of the meta data of this project.

	create_date = models.DateTimeField(auto_now_add = True, blank = True)

#Serializer for REST framework

from rest_framework import serializers

class csv_file_serializer(serializers.ModelSerializer):
    create_by = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )
    
    class Meta:
        model = csv_file
        fields = 'id create_by project_id session_id raw_csv_file'.split()
        read_only_fields = 'id project_id session_id'.split()
        write_only_fields = 'raw_csv_file'.split()
        
