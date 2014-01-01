from django.contrib.auth.models import User
from collections import defaultdict
from library.models import library, compound
from django.core.exceptions import ObjectDoesNotExist
#from astropy.table import Table
import pandas as pd
import datetime as dt

from main.models import project, submission

class rawdatafile():#a base class for all file format
    def __init__(self,formdata):
        """formdata is the django UploadFileForm in main.models
        pandas is used to parse the datafile"""   
        
        self.library_obj=formdata['library_pointer']
        self.library=self.library_obj.library_name if self.library_obj else formdata['library']

        self.formdata=formdata
        
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
        self.read_file()
        self.wells=self.p.plate.numofwells
        self.table_reg=dict()


    def read_file(self):
        filetype=self.formdata['datafile'].name.split(".")[-1]

        if filetype=='csv':
            self.rawdata=pd.read_csv(self.formdata['datafile'],header=None).fillna('').values
        #self.rawdata=pd.read_csv(formdata['datafile'],header=None).values.astype(str)
    

    def open_job_entry(self):
        """if everything is ready, create a pending job entry."""
        if self.p and self.rawdata.any():
            self.sub=submission(
                comments=self.formdata['comments'],
                jobtype='upload',
                project=project.objects.get(pk=self.formdata['project']),
                submit_by=User.objects.get(pk=self.formdata['user']),
                submit_time=self.datetime,
                log="plates in queue: %s"%self.formdata['plates'],
                status='p')
            self.sub.save()

    def update_job_status(self,log='',progress=0):
        """update logs and progress"""
        self.sub.log+=log#';plate: %s uploaded'%self.plates[pla]
        #self.sub.progress=progress
        self.sub.save()

    def close_job_entry(self):
        self.sub.status='c'
        self.sub.save()

    def report_job_fail(self):
        self.sub.status='f'
        self.sub.save()
    
    def is_table(self,row):#tell if within +- 2 row current posistion is a table, if so return the dimension of this table
        start=0
        for i in range(row-2,row+3):
            if '' not in self.rawdata[i]:
                x=len(self.rawdata[i])
                start=i
                break
        n=start

        while '' not in self.rawdata[n]:
            n+=1
        y=n-row
        
        if y<1:
            return False

        return {'start':start,'x':x,'y':y}

    def test(self):

        return self.rawdata[10]





class Envision_Grid_Reader(rawdatafile):

# process the data define where table are, also check if file is legit
# a.experiment.readout.all(), a.experiment.readout.count(), a.experiment.readout.get(name='FP').keywords
    def parse(self):
        n=0
        self.table_count=0
        for row in self.rawdata:#read through whole file and find out all the tables
            n+=1
            for m in self.readout.all():
                if m.keywords in row[0]:
                    result=self.is_table(n)
                    if result:
                        if result['x']>=len(self.col) and result['y']>=len(self.row):
                            self.table_reg[result['start']]=m.name
                            self.table_count+=1

        return self.table_reg
        
    def map_table(self):
        #creat pointers that point at each table

        replicate_count=0
        plate_count=0
        readout_list=list()

        if self.wells==384:
            
            if self.table_count < self.replicate_num*self.plates_num*self.readout_num:
                return False#raise exception might be good
            
            for i in sorted(self.table_reg):#go over each replicate and plate
                if self.table_reg[i] not in readout_list:
                    readout_list.append(self.table_reg[i]) 
                else:
                    readout_list=list()
                    readout_list.append(self.table_reg[i]) 
                    replicate_count+=1
                    if replicate_count==self.replicate_num:
                        replicate_count=0
                        plate_count+=1
                        if plate_count==self.plates_num:
                            break

                self.map[plate_count][replicate_count][self.table_reg[i]]=[i,1]
        
        elif self.wells==1536:

            if self.table_count*4 < self.replicate_num*self.plates_num*self.readout_num:
                return False#raise exception might be good

            for i in sorted(self.table_reg):#go over each replicate and plate
                if self.table_reg[i] not in readout_list:
                    readout_list.append(self.table_reg[i]) 
                else:
                    readout_list=list()
                    readout_list.append(self.table_reg[i]) 
                    replicate_count+=1
                    if replicate_count==self.replicate_num:
                        replicate_count=0
                        plate_count+=4
                        if plate_count>=self.plates_num:
                            break

                self.map[plate_count][replicate_count][self.table_reg[i]]=[i,1]
                self.map[plate_count+1][replicate_count][self.table_reg[i]]=[i,2]
                self.map[plate_count+2][replicate_count][self.table_reg[i]]=[i+1,1]
                self.map[plate_count+3][replicate_count][self.table_reg[i]]=[i+1,2]
        return self.map

    #save tables into database row by row, might take some time.
    def save(self):

        self.map_table()

        self.open_job_entry()
        
        exec ('from data.models import proj_'+str(self.proj_id)+' as data')
        for pla in range(self.plates_num):            

            for row in range(len(self.row)):

                for col in range(len(self.col)):

                    platewell=self.plates[pla]+self.row[row]+self.col[col]
                    
                    try:#check if this well has coresponding compound in our library
                        cmpd=compound.objects.get(plate_well = platewell,library_name=self.library_obj)
                    except ObjectDoesNotExist:
                        cmpd=None

                    #update_or_create: if same well already exists, it will be over written.
                    entry, created=data.objects.get_or_create(
                    library = self.library,
                    platewell=platewell,
                    plate = self.plates[pla],
                    well=self.row[row]+self.col[col],
                    project=self.p,
                    defaults={'submission':self.sub,
                              'create_date':self.datetime,
                              'create_by':self.sub.submit_by,
                              'compound_pointer':cmpd,
                              'library_pointer':self.library_obj}
                    )

                    entry.submission=self.sub
                    entry.create_date=self.datetime
                    entry.create_by=self.sub.submit_by
                    entry.compound_pointer=cmpd
                    entry.library_pointer=self.library_obj

                    for rep in range(self.replicate_num):#all the readouts
                    
                        for i in self.readout.all(): 
                            y=self.map[pla][rep][i.name][0]
                            x=self.map[pla][rep][i.name][1]

                            if self.wells==384:
                                exec('entry.%(readout)s_%(rep)s=self.rawdata[row+y][col+x]'%{'readout':i,'rep':self.replicate[rep]})
                            elif self.wells==1536:
                                exec('entry.%(readout)s_%(rep)s=self.rawdata[row*2+y][col*2+x]'%{'readout':i,'rep':self.replicate[rep]})

                    entry.save()
                            
            self.update_job_status(';plate: %s uploaded'%self.plates[pla])

        self.close_job_entry()
        return 'uploaded'
