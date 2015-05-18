from django.db import models
from django.contrib.auth.models import User
import uuid

#Create your models here.


class csv_file(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    create_by = models.ForeignKey(User,null=True,blank=True)

    create_date = models.DateTimeField(auto_now_add = True, blank = True)

    project_id = models.CharField(max_length=50,verbose_name='Project ID',blank=True)

    session_id = models.CharField(max_length=50,verbose_name='Session ID',blank=True)

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

    project_id = models.CharField(max_length=50,verbose_name='Project ID')
    
    create_date = models.DateTimeField(auto_now_add = True, blank = True)
    
    create_by = models.ForeignKey(User,null=True,blank=True)



#############################################################################################

#function to create a dynamic model
def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model


#function to create the table.
def install(model):
    from django.core.management import sql, color
    from django.db import connection

    # Standard syncdb expects models to be in reliable locations,
    # so dynamic models need to bypass django.core.management.syncdb.
    # On the plus side, this allows individual models to be installed
    # without installing the entire project structure.
    # On the other hand, this means that things like relationships and
    # indexes will have to be handled manually.
    # This installs only the basic table definition.

    # disable terminal colors in the sql statements
    style = color.no_style()

    cursor = connection.cursor()
    statements, pending = sql.sql_model_create(model, style)
    for sql in statements:
        cursor.execute(sql)


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
        
