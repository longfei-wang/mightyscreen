#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib.auth.models import User
from collections import defaultdict
#from astropy.table import Table
import pandas as pd
import datetime as dt

from celery.decorators import task

from main.models import project, submission, submission_plate_list



class rawdata():
    def __init__(self,formdata,sub):
#        self.rawdata = Table.read(csvfile,format='ascii')
        self.rawdata=pd.read_csv(formdata['datafile'],header=None).values.astype(str)
        self.library=formdata['library']
        self.plates=formdata['plates'].split(',')
        self.plates_num=len(self.plates)
        self.p=sub.project
        self.replicate=self.p.rep()
        self.readout=self.p.experiment.readout
        self.readout_num=self.readout.count()
        self.replicate_num=len(self.replicate)
        self.map=defaultdict(lambda: defaultdict(dict))
        self.datetime=sub.submit_time
        self.row=self.p.plate.row()
        self.col=self.p.plate.col()
        self.sub=sub

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
        exec ('from data.models import proj_'+str(self.p.pk)+' as data')
        for pla in range(self.plates_num):
            #csub the submission_palte_list entry for this plate
            csub=submission_plate_list(library=self.library,plate=self.plates[pla],submission_id=self.sub)
            #check if there is already a plate
            if submission_plate_list.objects.filter(library=self.library,plate=self.plates[pla],status='s'):
                
                csub.status='f'
                csub.messages+='plate '+str(pla)+' already exists!<br>'
                
            
            else:
    
                for rep in range(self.replicate_num):
    
                    for row in range(len(self.row)):
    
                        for col in range(len(self.col)):
                            
                            entry=data(
                            submission=self.sub,
                            library = self.library,
                            plate = self.plates[pla],
                            well=self.row[row]+self.col[col],
                            replicate=self.replicate[rep],
                            project=self.p,
                            create_date=self.datetime,
                            create_by=self.sub.submit_by,
                            )

                            
                            for i in self.readout.all(): 
                                j=self.map[pla][rep][i.name.encode('utf8')]
                                exec('entry.'+i.name+'=self.rawdata[row+j][col+1]')
#                                readout=data_readout(
#                                data_entry=entry,
#                                readout=i,
#                                reading=self.rawdata[row+j][col+1],
#                                )
#                                readout.save()

                            entry.save()
                            
                csub.status='s'
                
            csub.save()
            self.sub.status='c'
            self.sub.save(update_fields=['status'])
        return 'saved'


#wrap  rawdata class in a function for easier queue.
@task()
def submit_queue(*args):
    data = rawdata(*args)
    data.parse()
    data.save()
    return "parsed"
    
def submit_data(formdata):
    #create a entries in submission.
    sub=submission(comments=formdata['comments'],
                      project=project.objects.get(pk=formdata['project']),
                      submit_by=User.objects.get(pk=formdata['user']),
                      submit_time=dt.datetime.now(),
                      status='p')
    sub.save()

    #then parse_data in background
    submit_queue.delay(formdata,sub)
    
    return 'submitted'
