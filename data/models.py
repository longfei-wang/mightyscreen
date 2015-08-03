from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework import serializers
from django.core.serializers.json import DjangoJSONEncoder
import uuid, os
import json
from django.shortcuts import get_object_or_404
#Create your models here.

class JSONField(models.TextField):
    """
    JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly.
    Django snippet #1478

    example:
        class Page(models.Model):
            data = JSONField(blank=True, null=True)


        page = Page.objects.get(pk=5)
        page.data = {'title': 'test', 'type': 3}
        page.save()
    """

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if value == "":
            return None
        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass
        return value

    def get_db_prep_save(self, value, *args, **kwargs):
        if value == "":
            return None
        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return super(JSONField, self).get_db_prep_save(value, *args, **kwargs)







class project(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

	name = models.CharField(max_length=10,verbose_name='Project Name',default='Untitled')

	memo = models.TextField(blank=True)

	user = models.ForeignKey(User,null=True,blank=True)

	meta = JSONField(blank=True,null=True)#this stores a dictionary of the meta data of this project.

	create_date = models.DateTimeField(auto_now_add = True, blank = True)


def find_or_create_project(request):
    """
    find the project instance based on request
    if can't find any, create one and return the new project
    """

    if project.objects.filter(user=request.user).exists():
        
        p = project.objects.filter(user=request.user)[0]

        request.session['project'] = p.id.hex

    elif project.objects.filter(id=request.session.get('project', None)).exists(): #if cannot find project

        p = project.objects.get(id=request.session.get('project', None))
    
    else:

        p = project(user=None if request.user.is_anonymous() else request.user) #anonymouse user cannot be saved as a user object

        p.save()

        request.session['project'] = p.id.hex #set the session project keyword

    return p


def get_curPlate(request):
	"""
	A function to get current plate number
	"""
	def get_firstPlate(request):

		p = get_object_or_404(project,id=request.session.get('project',None))

		pdata = data.objects.filter(project=p)
		
		plate_list = [ i['plate'] for i in pdata.order_by('plate').values('plate').distinct()]

		return plate_list[0] if plate_list != [] else None

	#check request
	plate = request.GET.get('plate',
		request.session.get('plate',
				get_firstPlate(request)
			)
		)

	#set the plate number in session
	if plate:
		request.session['plate'] = plate

	return plate

#overwrite class from pytoolbox
class OverwriteMixin(object):
    """Update get_available_name to remove any previously stored file (if any) before returning the name."""

    def get_available_name(self, name):
        self.delete(name)
        return name



class OverwriteFileSystemStorage(OverwriteMixin, FileSystemStorage):
	"""A file-system based storage that let overwrite files with the same name."""



def get_file_name(instance,filename):
	"""
	This convert a filename to a unique filename
	"""
	return os.path.join(settings.CSV_FILE_DIR,uuid.uuid4().hex+'.csv')



class csv_file(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    create_date = models.DateTimeField(auto_now_add = True, blank = True)

    project = models.ForeignKey('project',null=True,blank=True)

    raw_csv_file = models.FileField(null=True,upload_to=get_file_name)

    cleaned_csv_file = models.FileField(null=True,blank=True,upload_to=settings.CSV_FILE_DIR,storage=OverwriteFileSystemStorage())


#Serializer for REST framework


class csv_file_serializer(serializers.ModelSerializer):

    
    class Meta:
        model = csv_file
        fields = 'id project raw_csv_file'.split()
        read_only_fields = 'id project'.split()
        write_only_fields = 'raw_csv_file'.split()

# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

@receiver(pre_delete, sender=csv_file)
def csv_file_delete(sender, instance, **kwargs):
	"""
	make sure when csv_file model is deleted the files get deleted too.
	"""
	# Pass false so FileField doesn't save the model.
	instance.raw_csv_file.delete(False)
	instance.cleaned_csv_file.delete(False)


#Data object abstract for all screening raw data. Real table is in app:data
#Two ways of identify compound. FaciclityID? or Plate+Well
class data_base(models.Model):
    
    def __unicode__(self):
    
        return self.library+self.plate_well
        
    class Meta:

        abstract=True
        unique_together = ('plate_well','project')
        index_together = ['plate_well','project']
    
    library = models.CharField(max_length=50,verbose_name='Library')

    plate_well = models.CharField(max_length=50)#using plate well as unique identifier, not good for more than one libraries

    plate = models.IntegerField()

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
	readout10 = models.FloatField(null=True,blank=True)
	readout11 = models.FloatField(null=True,blank=True)
	readout12 = models.FloatField(null=True,blank=True)

    
#the serializer for data
class DataSerializer(serializers.ModelSerializer):

    class Meta:
        model = data
        fields = 'plate_well plate well hit welltype create_date readout1 readout2 readout3 \
        readout4 readout5 readout6 readout7 readout8 readout9 readout10 readout11 readout12'.split()


import django_filters

#filter class for data
class DataFilter(django_filters.FilterSet):
    class Meta:
        model = data
        fields = 'plate well hit plate_well welltype readout1 readout2 readout3 readout4 \
        readout5 readout6 readout7 readout8 readout9 readout10 readout11 readout12'.split()
