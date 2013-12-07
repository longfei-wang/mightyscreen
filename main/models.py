#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ReadoutListField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(ReadoutListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return value.split(self.token)

    def get_db_prep_value(self, value, connection, prepared = False):
        if not value: return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


#define a screening project
class project(models.Model):
    def __unicode__(self):
        return self.name
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField()
    agreement = models.CharField(max_length=20)
    experiment = models.ForeignKey('experiment')
    plate = models.ForeignKey('plate')
    replicate = ReadoutListField()
    fileformat = models.ForeignKey('fileformat')
    user = models.ManyToManyField(User)


#define a experiemnt
class experiment(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=20)
    description =  models.TextField()
    readout = models.ManyToManyField('readout')


#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class readout(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=255)
    description = models.TextField()
    keywords = ReadoutListField()


#the format of the file user upload.
class fileformat(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=20)


#All the plate types.
class plate(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=20)
    numofwells = models.PositiveIntegerField()
    columns = ReadoutListField()
    rows = ReadoutListField()
    ochoice = (
    ('TL','top-left'),
    ('TR','top-right'),
    ('BL','bottom-left'),
    ('BR','bottom-right'),
    )
#    origin = models.CharField(max_length=2, choices=ochoice)

class submission(models.Model):
    submission_id=models.ForeignKey('submission_id')
    project=models.ForeignKey('project')
    datetime = models.DateTimeField()
    submit_by = models.ForeignKey(User)
    library = models.CharField(max_length=20)
    plate=models.CharField(max_length=10)
    message=models.TextField(blank=True)
    schoice = (
    ('p','pending'),
    ('f','failed'),
    ('s','succeed'),
    )
    status=models.CharField(max_length=1, choices=schoice)
    
class submission_id(models.Model):
    description = models.TextField(blank=True)
    
#class well(models.Model):
#    #a table describing plate format and each position of wells in this plate, dosen't nessesarily need to be a plate, could be anything.
#    def __unicode__(self):
#        return self.plate_type        
#    plate_type = models.ForeignKey('plate')
#    column = models.CharField(max_length=10)
#    row = models.CharField(max_length=10)
#    position = models.CharField(max_length=20)

#Data object for all screening raw data, readout is stored in comma seperated array, well posistion is refering another table   
class data(models.Model):
    def __unicode__(self):
        return self.readout
    ID = models.AutoField(primary_key=True)
    library = models.CharField(max_length=20)
    plate = models.CharField(max_length=10)
    well = models.CharField(max_length=10)
    replicate = models.CharField(max_length=10)
    project = models.ForeignKey('project')
    submission_id=models.ForeignKey('submission_id')
    readout =  ReadoutListField()
    datetime = models.DateTimeField()
    create_by = models.ForeignKey(User)




#==============================================================================
## test models from QY

#class for uploaded files
class rawDataFile(models.Model):
    def __unicode__(self):
        return self.readout
    
    datafile = models.FileField(upload_to = 'rawdata_test_%Y%m%d')
    

class compound(models.Model):
    def __unicode__(self):
        return (self.library_name + ' '+ self.plate_well)      
    library_name = models.ForeignKey('library')
    sub_library_name = models.ForeignKey('sub_library')
    facility_reagent_id = models.CharField(max_length = 30)
    plate = models.IntegerField(default=0)
    well = models.CharField(max_length = 20)
    plate_well = models.CharField(max_length = 20)
    pubchem_cid = models.IntegerField(default=0)
    chemical_name = models.CharField(max_length = 30)
    molecular_weight = models.DecimalField(max_digits=10, decimal_places=5)
    formula = models.CharField(max_length = 30)
    tpsa = models.DecimalField(max_digits=8, decimal_places=2)
    logp = models.DecimalField(max_digits=8, decimal_places=4)
    inchikey = models.CharField(max_length = 30)
    canonical_smiles = models.CharField(max_length = 100)
    inchi = models.TextField()
    fp2 = models.TextField()
    fp3 = models.CharField(max_length = 50)
    fp4 = models.TextField()
    svg = models.TextField()
    sdf = models.TextField()
#    additional_properties = models.ForeignKey('additional_compound_info')

class additional_compound_info(models.Model):
    pass

class library(models.Model):
    def __unicode__(self):
        return self.library_name
    library_name = models.CharField(max_length = 30)
    sub_librarys = models.CharField(max_length = 30)
    compounds = models.CharField(max_length = 30)    
    
class sub_library(models.Model):
    def __unicode__(self):
        return self.sub_library_name 
    sub_library_name = models.CharField(max_length = 30)
    super_library = models.ForeignKey('library') 
    compounds = models.CharField(max_length = 30)

        
    
    

