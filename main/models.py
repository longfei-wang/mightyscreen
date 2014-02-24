#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from mongoengine import *
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
        return [i[0] for i in self.readout.values_list('name')]
    def scores(self):
        return [i[0] for i in self.score.values_list('name')]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    primary_key = models.CharField(max_length=100,default='platewell')
    plate = models.ForeignKey('plate',null=True,blank=True)
    replicate = models.PositiveSmallIntegerField(verbose_name='num of replicates',default=1)

    readout = models.ManyToManyField('readout',null=True,blank=True)
    score = models.ManyToManyField('score',null=True,blank=True)
    
    leader = models.ForeignKey(User,related_name='proj_leader')
    user = models.ManyToManyField(User,null=True,blank=True)
    deleted = models.BooleanField(default=False)
   

# this is a table define score function of a experiment
class score(models.Model):
    def __unicode__(self):
        return self.name

    def __init__(self,*args,**kwargs):
        super(score,self).__init__(*args,**kwargs)
        if self.template:
            self.formula = self.template.formula

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    isfilter=models.BooleanField(default=False,verbose_name='This is a filter')#define if this is a filter
    
    key = models.CharField(max_length=100,verbose_name='Input Vars')
    template=models.ForeignKey('score_template',null=True,blank=True)
    formula = models.CharField(max_length=200,blank=True)
    

    create_by = models.ForeignKey(User)

# score template
class score_template(models.Model):
    def __unicode__(self):
        return self.name+':'+self.description

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    formula = models.CharField(max_length=200)


#since differnet experiment has different readouts, this is a table define specific readout of a experiment
class readout(models.Model):
    def __unicode__(self):
        return self.name
    
    def __init__(self,*args,**kwargs):
        super(readout,self).__init__(*args,**kwargs)
        if self.template:
            self.identifier=self.template.identifier

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    template=models.ForeignKey('readout_template',null=True,blank=True)
    identifier = models.CharField(max_length=200,blank=True)
    create_by = models.ForeignKey(User)


#readout template
class readout_template(models.Model):
    def __unicode__(self):
        return self.name+':'+self.description
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    identifier = models.CharField(max_length=200)


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
