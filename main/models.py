#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django import forms

# Create your models here.

#define a screening, basically list of projects with their relations. like primary screen, secondary screen.
class screen(models.Model):
    pass

#define a screening sub project
class project(models.Model):
    def __unicode__(self):
        return self.name
    def rep(self):
        return self.replicate.split(',')
    
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    agreement = models.CharField(max_length=50)
    experiment = models.ForeignKey('experiment')
    plate = models.ForeignKey('plate')
    replicate = models.CharField(max_length=50)
    score = models.ManyToManyField('score',blank=True)
    leader = models.ForeignKey(User,related_name='leader')
    user = models.ManyToManyField(User)

        
#define a experiemnt
class experiment(models.Model):
    def __unicode__(self):
        return self.name        
    
    name = models.CharField(max_length=50)
    description =  models.TextField(blank=True)
    readout = models.ManyToManyField('readout')



#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class score(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    formular = models.TextField()


#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class readout(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    keywords = models.TextField()


#the format of the file user upload.
class fileformat(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=50)


#All the plate types.
class plate(models.Model):
    def __unicode__(self):
        return self.name

    def col(self):
        return self.columns.split(',')
    def row(self):
        return self.rows.split(',')
    def well(self):
        well=list()
        for i in self.row():
            for j in self.col():
                well.append(i+j)
        return well

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

#job list/track table
class submission(models.Model):
    def __unicode__(self):
        return self.get_status_display()
    jobtype=models.CharField(max_length=20)
    project=models.ForeignKey('project')
    submit_time = models.DateTimeField()
    submit_by = models.ForeignKey(User)
    comments=models.TextField(blank=True)
    log=models.TextField(blank=True)
    schoice = (
    ('p','pending'),
    ('c','complete'),
    )
    status=models.CharField(max_length=1, choices=schoice)

#Table record all the plates submitted to the database. Do we really need it? Naah. Use group by
# class submission_plate_list(models.Model):
#     def __unicode__(self):
#         return self.plate
#     submission=models.ForeignKey('submission')
#     project=models.ForeignKey('project')
#     library = models.CharField(max_length=50)
#     plate=models.CharField(max_length=50)

#Data object abstract for all screening raw data. Real table is in app:data
#Two ways of identify compound. FaciclityID? or Plate+Well
class data_base(models.Model):
    def __unicode__(self):
        return self.well
    class Meta:
        abstract=True
    library = models.CharField(max_length=50)
    plate = models.CharField(max_length=20)
    well = models.CharField(max_length=20)

    schoice = (
    ('E','empty'),
    ('P','positive control'),
    ('N','negative control'),
    ('B','bad well'),
    ('X','compound'),
    )
    welltype=models.CharField(max_length=1,choices=schoice,default='X')

    project = models.ForeignKey('project')
    submission=models.ForeignKey('submission')
    create_date = models.DateTimeField()
    create_by = models.ForeignKey(User)

class UploadFileForm(forms.Form):
    
    #title = forms.CharField(max_length=50)
    project = forms.CharField(widget=forms.HiddenInput)
    user = forms.CharField(widget=forms.HiddenInput)
    library = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Library Name'}))
    plates = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Plates List, like 1,2,3 '}))
    datafile  = forms.FileField(widget=forms.FileInput())
    comments = forms.CharField(widget=forms.Textarea(),required=False)


