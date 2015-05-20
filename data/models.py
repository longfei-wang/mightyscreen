from django.db import models
from django.contrib.auth.models import User
import uuid

#Create your models here.

class project(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	name = models.CharField(max_length=10,verbose_name='Project Name',blank=True)

	memo = models.TextField(blank=True)

	user = models.ForeignKey(User,null=True,blank=True)

	session = models.CharField(max_length=50,verbose_name='Session Key',blank=True)

	meta = models.TextField(blank=True)#this stores a dictionary of the meta data of this project.

	create_date = models.DateTimeField(auto_now_add = True, blank = True)


def find_or_create_project(request):
	"""
	find the project instance based on request
	if can't find any, create one and return the new project
	"""
	if not request.session.exists(request.session.session_key):#make sure session key is not None
	
		request.session.create()

	if project.objects.filter(id=request.session.get('project', None)).exists(): #if cannot find project
			
		p = project.objects.get(id=request.session.get('project', None))

	elif project.objects.filter(session=request.session.session_key).exists(): #if cannot find session

		p = project.objects.get(session=request.session.session_key)

	else:

		p = project(user=None if request.user.is_anonymous() else request.user, #anonymouse user cannot be saved as a user object
					session=request.session.session_key)
		p.save()

	return p

class csv_file(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    create_date = models.DateTimeField(auto_now_add = True, blank = True)

    project = models.ForeignKey('project',null=True,blank=True)

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


class data(data_base):

	readout1 = models.FloatField(null=True,blank=True)
	readout2 = models.FloatField(null=True,blank=True)
	readout3 = models.FloatField(null=True,blank=True)
	readout4 = models.FloatField(null=True,blank=True)
	readout5 = models.FloatField(null=True,blank=True)
	readout6 = models.FloatField(null=True,blank=True)
	readout7 = models.FloatField(null=True,blank=True)
	readout8 = models.FloatField(null=True,blank=True)
	readout9 = models.FloatField(null=True,blank=True)
    

#Serializer for REST framework

from rest_framework import serializers

class csv_file_serializer(serializers.ModelSerializer):

    
    class Meta:
        model = csv_file
        fields = 'id project raw_csv_file'.split()
        read_only_fields = 'id project'.split()
        write_only_fields = 'raw_csv_file'.split()
        
