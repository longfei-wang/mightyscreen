from django import forms
from django.contrib.auth.models import User
from collections import defaultdict
#from astropy.table import Table
import pandas as pd
import datetime

from main.models import project, data, experiment, readout, fileformat, plate



class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class readrawdata():
    def __init__(self,csvfile,project_name,user_name,plates):
#        self.rawdata = Table.read(csvfile,format='ascii')
        self.rawdata=pd.read_csv(csvfile,header=None).values.astype(str)
        self.user_name=user_name
        self.plates=plates
        self.plates_num=len(plates)
        self.p=project.objects.get(name=project_name)
        self.replicate=self.p.replicate
        self.readout=self.p.experiment.readout
        self.readout_num=self.readout.count()
        self.replicate_num=len(self.replicate)
        self.map=defaultdict(lambda: defaultdict(dict))
        self.datetime=datetime.datetime.now()

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
            for rep in range(len(self.replicate)):
                for row in range(len(self.p.plate.rows)):
                    for col in range(len(self.p.plate.columns)):
                        readout_list = list()
                        for i in self.readout.all(): 
                            j=self.map[pla][rep][i.name.encode('utf8')]
                            readout_list.append(self.rawdata[row+j][col+1])
                        entry = data(
                        library = '',
                        plate = self.plates[pla],
                        well=self.p.plate.rows[row]+self.p.plate.columns[col],
                        replicate=self.replicate[rep],
                        project=self.p,
                        readout=','.join(readout_list),
                        datetime=self.datetime,
                        create_by=User.objects.get(username__exact=self.user_name),
                        )
                        #entry.save()
        return 'saved'
        
        
