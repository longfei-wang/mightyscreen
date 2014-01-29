#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from library.models import library as lib, compound
from library.models import *
# Create your models here.

#define a screening flow chart, basically list of projects with their relations. like primary screen, secondary screen.
class project_relation(models.Model):
    project = models.ForeignKey('project')
    project_related = models.ForeignKey('project',related_name='prelated')
    schoice = (
            ('c','child'),
            ('s','sibling'))#no need to put parent here, will be duplicate?
    relation = models.CharField(max_length=2,choices=schoice)

#define a screening sub project
class project(models.Model):

    rep_namespace='A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()

    def __unicode__(self):
        return self.name
    def rep(self):
        return self.rep_namespace[:self.replicate]
    def readouts(self):
        return [i[0] for i in self.experiment.readout.values_list('name')]
    def scores(self):
        return [i[0] for i in self.score.values_list('name')]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    agreement = models.CharField(max_length=50,blank=True)
    experiment = models.ForeignKey('experiment')
    plate = models.ForeignKey('plate')
    replicate = models.PositiveSmallIntegerField(verbose_name='num of replicates')
    score = models.ManyToManyField('score',blank=True)
    leader = models.ForeignKey(User,related_name='leader')
    user = models.ManyToManyField(User)
    deleted = models.BooleanField(default=False)
   
#define a experiemnt
class experiment(models.Model):
    def __unicode__(self):
        return self.name        
    
    name = models.CharField(max_length=50)
    description =  models.TextField(blank=True)
    readout = models.ManyToManyField('readout')
    create_by = models.ForeignKey(User)



#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class score(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    #isfilter=models.BooleanField()#define if this is a filter
    formular = models.TextField()
    create_by = models.ForeignKey(User)

#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class readout(models.Model):
    def __unicode__(self):
        return self.name        
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    keywords = models.TextField()
    create_by = models.ForeignKey(User)

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
    numofwells = models.PositiveSmallIntegerField()
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
        return str(self.pk)
    def log_to_html(self):
        log=[]
        for i in self.log.split('.'):
            if len(i)>80:
                log.append(i[:77]+'...<br>')
            else:
                log.append(i[:80]+'<br>')
        return ''.join(log)

    jobtype=models.CharField(max_length=20)
    project=models.ForeignKey('project')
    submit_time = models.DateTimeField()
    submit_by = models.ForeignKey(User)
    comments=models.TextField(blank=True)
    progress=models.PositiveSmallIntegerField(default=0)#percentage?
    result=models.FileField(upload_to='job_results',blank=True,null=True)
    log=models.TextField(blank=True)
    schoice = (
    ('p','pending'),
    ('c','complete'),
    ('f','fail')
    )
    status=models.CharField(max_length=1, choices=schoice)

class view(Document):#save a view for sharing purpose.
    query = StringField()
    field_list = StringField()
    user_id = IntField()
    proj_id = IntField()
