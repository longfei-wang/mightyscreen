#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#class ReadoutListField(models.TextField):
#    __metaclass__ = models.SubfieldBase
#
#    def __init__(self, *args, **kwargs):
#        self.token = kwargs.pop('token', ',')
#        super(ReadoutListField, self).__init__(*args, **kwargs)
#
#    def to_python(self, value):
#        if not value: return
#        if isinstance(value, list):
#            return value
#        return value.split(self.token)
#
#    def get_db_prep_value(self, value, connection, prepared = False):
#        if not value: return
#        assert(isinstance(value, list) or isinstance(value, tuple))
#        return self.token.join([unicode(s) for s in value])
#
#    def value_to_string(self, obj):
#        value = self._get_val_from_obj(obj)
#        return self.get_db_prep_value(value)


#define a screening project
class project(models.Model):
    def __unicode__(self):
        return self.name
    
    name = models.CharField(max_length=50)
    description = models.TextField()
    agreement = models.CharField(max_length=20)
    experiment = models.ForeignKey('experiment')
    plate = models.ForeignKey('plate')
    replicate = models.TextField()
    score = models.ManyToManyField('score')
    ower = models.ForeignKey(User)
    user = models.ManyToManyField(User)

    def rep(self):
        return self.replicate.split(',')
        
#define a experiemnt
class experiment(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description =  models.TextField()
    readout = models.ManyToManyField('readout')



#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class score(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description = models.TextField()
    formular = models.TextField()


#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class readout(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description = models.TextField()
    keywords = models.TextField()


#the format of the file user upload.
class fileformat(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=20)


#All the plate types.
class plate(models.Model):
    def __unicode__(self):
        return self.name

    def col(self):
        return self.columns.split(',')
    def row(self):
        return self.rows.split(',')
    
    name = models.CharField(max_length=50)
    numofwells = models.PositiveIntegerField()
    columns = models.TextField()
    rows = models.TextField()
    ochoice = (
    ('tl','top-left'),
    ('tr','top-right'),
    ('bl','bottom-left'),
    ('br','bottom-right'),
    )
    origin = models.CharField(max_length=2, choices=ochoice)

class submission(models.Model):
    def __unicode__(self):
        return self.get_status_display()
    project=models.ForeignKey('project')
    submit_time = models.DateTimeField()
    submit_by = models.ForeignKey(User)
    comments=models.TextField(blank=True)
    schoice = (
    ('p','pending'),
    ('c','complete'),
    )
    status=models.CharField(max_length=1, choices=schoice)
    
class submission_plate_list(models.Model):
    def __unicode__(self):
        return self.get_status_display()
    submission_id=models.ForeignKey('submission')
    library = models.CharField(max_length=50)
    plate=models.CharField(max_length=50)
    schoice = (
    ('f','failed'),
    ('s','succeed'),
    )
    status=models.CharField(max_length=1, choices=schoice)
    messages = models.TextField(blank=True)

#Data object for all screening raw data, readout is stored in comma seperated array, well posistion is refering another table   
#class data(models.Model):
#    def __unicode__(self):
#        return self.readout
#    library = models.CharField(max_length=20)
#    plate = models.CharField(max_length=10)
#    well = models.CharField(max_length=10)
#    replicate = models.CharField(max_length=10)
#    project = models.ForeignKey('project')
#    submission=models.ForeignKey('submission')
#    create_date = models.DateTimeField()
#    create_by = models.ForeignKey(User)
#    def _get_readout(self):
#        return data_readout.objects.filter(data_entry=self)
#    readout=property(_get_readout)
#
#class data_readout(models.Model):
#    def __unicode__(self):
#        return self.reading
#    data_entry=models.ForeignKey('data')
#    readout=models.ForeignKey('readout')
#    reading=models.TextField()

class data_base(models.Model):
    def __unicode__(self):
        return self.readout
    class Meta:
        abstract=True
    library = models.CharField(max_length=50)
    plate = models.CharField(max_length=20)
    well = models.CharField(max_length=20)
    replicate = models.CharField(max_length=20)

    schoice = (
    ('E','empty'),
    ('P','positive control'),
    ('N','negative control'),
    ('B','bad well'),
    ('X','compound'),
    )
    welltype=models.CharField(max_length=1, choices=schoice)

    project = models.ForeignKey('project')
    submission=models.ForeignKey('submission')
    create_date = models.DateTimeField()
    create_by = models.ForeignKey(User)

    
    

