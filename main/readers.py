from django.contrib.auth.models import User
from collections import defaultdict
#from astropy.table import Table
import pandas as pd
import datetime as dt

from main.models import project, submission

class rawdatafile():#a base class for all file format
    def __init__(self,formdata):
        """formdata is the django UploadFileForm in main.models
        pandas is used to parse the datafile"""   
        
        self.formdata=formdata
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

        self.read_file()


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
        self.sub.log+=';plate: %s uploaded'%self.plates[pla]
        #self.sub.progress=progress
        self.sub.save()

    def close_job_entry(self):
        self.sub.status='c'
        self.sub.save()

    def test(self):

        return self.rawdata[10]





class Envision_Grid_Reader(rawdatafile):

# process the data define where table are, also check if file is legit
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
        



#save tables into database row by row, might take some time.
    def save(self):

        self.open_job_entry()
        
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

                    for rep in range(self.replicate_num):#all the readouts
                    
                        for i in self.readout.all(): 
                            j=self.map[pla][rep][i.name.encode('utf8')]
                            exec('entry.%(readout)s_%(rep)s=self.rawdata[row+j][col+1]'%{'readout':i,'rep':self.replicate[rep]})

                    entry.save()
                            
            self.update_job_status(';plate: %s uploaded'%self.plates[pla])

        self.close_job_entry()
        return 'uploaded'
