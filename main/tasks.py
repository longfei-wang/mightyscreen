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

from main.models import project, data, submission, submission_id
from main.models import compound, additional_compound_info, library, sub_library



class UploadFileForm(forms.Form):
    """to longfei: I change the name from file to datafile
    because file is a type name, could cause error"""
        
    #title = forms.CharField(max_length=50)
    datafile  = forms.FileField()

class parsedata():
    def __init__(self,csvfile,project_name,user_name,library_name,plates_array,sub_id):
#        self.rawdata = Table.read(csvfile,format='ascii')
        self.rawdata=pd.read_csv(csvfile,header=None).values.astype(str)
        self.user_name=user_name
        self.library=library_name
        self.plates=plates_array
        self.plates_num=len(plates_array)
        self.p=project.objects.get(name=project_name)
        self.replicate=self.p.replicate
        self.readout=self.p.experiment.readout
        self.readout_num=self.readout.count()
        self.replicate_num=len(self.replicate)
        self.map=defaultdict(lambda: defaultdict(dict))
        self.datetime=dt.datetime.now()
        self.sub=submission_id.objects.get(pk=sub_id)
            




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

                if m.keywords[0] in row[0]:
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

        
#class data(models.Model):
#    def __unicode__(self):
#        return self.readout
#    ID = models.AutoField(primary_key=True)
#    library = models.CharField(max_length=20)
#    plate = models.CharField(max_length=10)
#    well = models.CharField(max_length=10)
#    replicate = models.CharField(max_length=10)
#    project = models.ForeignKey('project')
#    readout =  ReadoutListField()
#    datetime = models.DateTimeField()
#    create_by = models.OneToOneField(User)


#save tables into database row by row, might take some time.
    def save(self):

        for pla in range(len(self.plates)):
            #csub the submission entry for this plate
            csub=submission.objects.get(project=self.p,library=self.library,plate=self.plates[pla],submission_id=self.sub)
            #check if there is already a plate
            if submission.objects.filter(project=self.p,library=self.library,plate=self.plates[pla],status='s'):
                
                csub.status='f'
                csub.message+='plate '+str(pla)+' already exists!<br>'
                csub.save(update_fields=['status','message'])
            
            else:
    
                for rep in range(len(self.replicate)):
    
                    for row in range(len(self.p.plate.rows)):
    
                        for col in range(len(self.p.plate.columns)):
                            readout_list = list()
    
                            for i in self.readout.all(): 
                                j=self.map[pla][rep][i.name.encode('utf8')]
                                readout_list.append(self.rawdata[row+j][col+1])
    
                            entry = data(
                            submission_id=self.sub,
                            library = self.library,
                            plate = self.plates[pla],
                            well=self.p.plate.rows[row]+self.p.plate.columns[col],
                            replicate=self.replicate[rep],
                            project=self.p,
                            readout=','.join(readout_list),
                            datetime=self.datetime,
                            create_by=User.objects.get(username__exact=self.user_name),
                            )
    
                            entry.save()
                            
                csub.status='s'
                csub.save(update_fields=['status'])
                
        return 'saved'

#wrap  rawdata class in a function for easier queue.
@task()
def parse_data(*args):
    rawdata = parsedata(*args)
    rawdata.parse()
    rawdata.save()
    return "parsed"

#class submission(models.Model):
#    submission_id=models.ForeignKey('submission_id')
#    project=models.ForeignKey('project')
#    datetime = models.DateTimeField()
#    submit_by = models.ForeignKey(User)
#    library = models.CharField(max_length=20)
#    plate=models.CharField(max_length=10)
#    message=models.TextField(blank=True)
#    status = (
#    ('p','pending'),
#    ('f','failed'),
#    ('s','succeed'),
#    )
#    
#class submission_id(models.Model):
#    pass


    
def submit_data(csvfile,project_name,user_name,library_name,plates_array):
    #create a entries in submission.
    sub_id=submission_id(description='just a test')
    sub_id.save()
    time = dt.datetime.now()
    proj = project.objects.get(name=project_name)
    user = User.objects.get(username__exact=user_name)
    
    for i in plates_array:
        sub=submission(
        submission_id=sub_id,
        project=proj,
        datetime=time,
        submit_by=user,
        library=library_name,
        plate= i,
        status='p'
        )
        sub.save()

    #then parse_data in background
    parse_data.delay(csvfile,project_name,user_name,library_name,plates_array,sub_id.pk)
    
    return "submitted"
 
#=============================================================================
## Tasks from QY    
    
class compound_library(object):
    ''' library of compounds to be saved into database
    Input file is a list of each compound with all the properties stored as dictionary
    Input file normally generated using method library.updated_parsed_saved from another script
    '''        
    def __init__(self,formated_dic_lib_file):
        self._source = formated_dic_lib_file
        self._mols =[json.loads(mol) for mol in open(self._source, 'rU')] 
        self._name = self.get_mols()[0]['Library_Name']    
    
    def get_name(self):
        return self._name
    
    def get_source(self):
        return self._source
    
    def get_mols(self):
        return self._mols
    
    def save(self):
        '''import data into the database'''
        mols = self.get_mols()
        for mol in mols:
            entry = compound(
                tpsa = mol["TPSA"],
                library_name = mol["Library_Name"],
                inchikey = mol["InChiKey"],
                facility_reagent_id = mol["Facility_Reagent_ID"],
                plate_well = mol["Plate_Well"],
                logp = mol["logP"],
                plate = mol["Plate"],
                svg = mol["svg"],
                well = mol["Well"],
                molecular_weight = mol["Molecular_Weight"],
                library = mol["Library"],
                chemical_name = mol["Chemical_Name"],
                pubchem_cid = mol["PubChem_CID"],
                fp4 = mol["Fp4"],
                sdf = mol["sdf"],
                fp3 = mol["Fp3"],
                fp2 = mol["Fp2"],
                inchi = mol["InChI"],
                formula = mol["Formula"],
                canonical_smiles = mol["Canonical_Smiles"],
                )
            entry.save()
            
            entry = library(
                library_name = mol["Library_Name"],
                )
            entry.save()
            
            entry = sub_library(
                sub_library_name = mol["Library"],
                super_library_name = mol["Library_Name"],
                )
            entry.save()

class iccb_library(compound_library):
    def to_be_added():
        pass

def uploadIccbLibrary(jsonFile):
    lib = iccb_library(jsonFile)
    lib.save()
    return dir(uploadIccbLibrary)

