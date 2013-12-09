#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django import forms
from django.contrib.auth.models import User
from collections import defaultdict
#from astropy.table import Table
import pandas as pd
import datetime as dt
import json

from celery.decorators import task

from main.models import project, data, data_readout, submission, submission_plate_list


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
    
                            entry = data(
                            submission=self.sub,
                            library = self.library,
                            plate = self.plates[pla],
                            well=self.row[row]+self.col[col],
                            replicate=self.replicate[rep],
                            project=self.p,
                            create_date=self.datetime,
                            create_by=self.sub.submit_by,
                            )
    
                            entry.save()
                            
                            for i in self.readout.all(): 
                                j=self.map[pla][rep][i.name.encode('utf8')]
                                readout=data_readout(
                                data_entry=entry,
                                readout=i,
                                reading=self.rawdata[row+j][col+1],
                                )
                                readout.save()

                            
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
                      project=project.objects.get(name=formdata['project']),
                      submit_by=User.objects.get(username__exact=formdata['user']),
                      submit_time=dt.datetime.now(),
                      status='p')
    sub.save()

    #then parse_data in background
    submit_queue.delay(formdata,sub)
    
    return 'submitted'

 
#=============================================================================
## Tasks from QY    
    
#class compound_library(object):
#    ''' library of compounds to be saved into database
#    Input file is a list of each compound with all the properties stored as dictionary
#    Input file normally generated using method library.updated_parsed_saved from another script
#    '''        
#    def __init__(self,formated_dic_lib_file):
#        self._source = formated_dic_lib_file
#        self._mols =[json.loads(mol) for mol in open(self._source, 'rU')] 
#        self._name = self.get_mols()[0]['Library_Name']    
#    
#    def get_name(self):
#        return self._name
#    
#    def get_source(self):
#        return self._source
#    
#    def get_mols(self):
#        return self._mols
#    
#    def save(self):
#        '''import data into the database'''
#        mols = self.get_mols()
#        for mol in mols:
#            entry = compound(
#                tpsa = mol["TPSA"],
#                library_name = mol["Library_Name"],
#                inchikey = mol["InChiKey"],
#                facility_reagent_id = mol["Facility_Reagent_ID"],
#                plate_well = mol["Plate_Well"],
#                logp = mol["logP"],
#                plate = mol["Plate"],
#                svg = mol["svg"],
#                well = mol["Well"],
#                molecular_weight = mol["Molecular_Weight"],
#                library = mol["Library"],
#                chemical_name = mol["Chemical_Name"],
#                pubchem_cid = mol["PubChem_CID"],
#                fp4 = mol["Fp4"],
#                sdf = mol["sdf"],
#                fp3 = mol["Fp3"],
#                fp2 = mol["Fp2"],
#                inchi = mol["InChI"],
#                formula = mol["Formula"],
#                canonical_smiles = mol["Canonical_Smiles"],
#                )
#            entry.save()
#            
#            entry = library(
#                library_name = mol["Library_Name"],
#                )
#            entry.save()
#            
#            entry = sub_library(
#                sub_library_name = mol["Library"],
#                super_library_name = mol["Library_Name"],
#                )
#            entry.save()
#
#class iccb_library(compound_library):
#    def to_be_added():
#        pass
#
#def uploadIccbLibrary(jsonFile):
#    lib = iccb_library(jsonFile)
#    lib.save()
#    return dir(uploadIccbLibrary)



