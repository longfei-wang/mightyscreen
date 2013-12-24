#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib.auth.models import User
from collections import defaultdict
#from astropy.table import Table
import pandas as pd
import datetime as dt

from celery.decorators import task

from main.models import project, submission
from django import forms

class rawdatafile():
    def __init__(self,formdata):
        """formdata is the django UploadFileForm in main.models
        pandas is used to parse the datafile"""   
        filetype=formdata['datafile'].name.split(".")[-1]
        

        if filetype=='csv':
            self.rawdata=pd.read_csv(formdata['datafile'],header=None).fillna('').values
        #self.rawdata=pd.read_csv(formdata['datafile'],header=None).values.astype(str)
        self.library=formdata['library']
        self.proj_id=formdata['project']
        self.plates=formdata['plates'].split(',')
        self.plates_num=len(self.plates)
        self.p=project.objects.get(pk=formdata['project'])
        self.replicate=self.p.rep()
        self.readout=self.p.experiment.readout
        self.readout_num=self.readout.count()
        self.replicate_num=len(self.replicate)
        self.map=defaultdict(lambda: defaultdict(dict))
        self.datetime=dt.datetime.now()
        self.row=self.p.plate.row()
        self.col=self.p.plate.col()


        #if everything is ready, create a pending job entry.
        if self.p and self.rawdata.any():
            self.sub=submission(
                comments=formdata['comments'],
                jobtype='upload',
                project=project.objects.get(pk=formdata['project']),
                submit_by=User.objects.get(pk=formdata['user']),
                submit_time=self.datetime,
                log="plates in queue: %s"%formdata['plates'],
                status='p')
            self.sub.save()

# process the data define where table are
# a.experiment.readout.all(), a.experiment.readout.count(), a.experiment.readout.get(name='FP').keywords
    def parse(self):
        n=0
        readout_count=0
        replicate_count=0
        plate_count=0

        for row in self.rawdata:
            n+=1

            for m in self.readout.all():
                if m.keywords in row[0]:
                    self.map[plate_count][replicate_count][m.name.encode('utf8')]=n+1
                    readout_count+=1
                if readout_count==self.readout_num:
                    readout_count=0
                    replicate_count+=1
                if replicate_count==self.replicate_num:
                    replicate_count=0
                    plate_count+=1
                if plate_count==self.plates_num:
                    return True
        
        return  False
        
    def test(self):

        return self.rawdata[10]


#save tables into database row by row, might take some time.
    def save(self):
        exec ('from data.models import proj_'+str(self.proj_id)+' as data')
        for pla in range(self.plates_num):            

            for row in range(len(self.row)):

                for col in range(len(self.col)):
                    
                    #update_or_create: if same well already exists, it will be over written.
                    entry, created=data.objects.get_or_create(
                    library = self.library,
                    plate = self.plates[pla],
                    well=self.row[row]+self.col[col],
                    project=self.p,
                    defaults={'submission':self.sub,'create_date':self.datetime,'create_by':self.sub.submit_by}
                    )

                    entry.submission=self.sub
                    entry.create_date=self.datetime
                    entry.create_by=self.sub.submit_by

                    for rep in range(self.replicate_num):
                    
                        for i in self.readout.all(): 
                            j=self.map[pla][rep][i.name.encode('utf8')]
                            exec('entry.%(readout)s_%(rep)s=self.rawdata[row+j][col+1]'%{'readout':i,'rep':self.replicate[rep]})

                    entry.save()
                            
            self.sub.log+=';plate: %s uploaded'%self.plates[pla]

        self.sub.status='c'
        self.sub.save()
        return 'uploaded'


#wrap  rawdata class in a function for easier queue.
@task()
def submit_queue(d):
    d.save()
    return True


class UploadFileForm(forms.Form):
    def submit_data(self):
        #define the submission method here.
        d = rawdatafile(self.cleaned_data)
        if d.parse():
        #then parse_data in background
            submit_queue(d)
        return 'submitted'
    #title = forms.CharField(max_length=50)
    project = forms.CharField(widget=forms.HiddenInput)
    user = forms.CharField(widget=forms.HiddenInput)
    library = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Library Name'}))
    plates = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Plates List, like 1,2,3 '}))
    datafile  = forms.FileField(widget=forms.FileInput())
    comments = forms.CharField(widget=forms.Textarea(),required=False)


