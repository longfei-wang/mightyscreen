from django import forms
from collections import defaultdict
import csv

from main.models import project, data, experiment, readout, fileformat, plate



class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class readrawdata():
    def __init__(self,csvfile,project_name,user_name,plates):
        self.csv = csv.reader(csvfile)
        self.user_name=user_name
        self.plates=plates
        self.plates_num=len(plates)
        self.p=project.objects.get(name=project_name)
        self.replicate=self.p.replicate
        self.readout=self.p.experiment.readout
        self.readout_num=self.readout.count()
        self.replicate_num=len(self.replicate)
        self.map=defaultdict(lambda: defaultdict(dict))
        

    def parse(self):
            
        # a.experiment.readout.all(), a.experiment.readout.count(), a.experiment.readout.get(name='FP').keywords
        n=0
        readout_count=0
        replicate_count=0
        plate_count=0
        for row in self.csv:
            n+=1
            for x in self.readout.all():
                if x.keywords[0] in row[0]:
                    self.map[plate_count][replicate_count][x.name]=n+1
                    readout_count+=1
                if readout_count==self.readout_num:
                    readout_count=0
                    replicate_count+=1
                if replicate_count==self.replicate_num:
                    replicate_count=0
                    plate_count+=1
                if plate_count==self.plates_num:
                    return list(self.map)

        return  False
    
#    def parse_table(self,row_num,readout):
#        n=row_num+1
#        for i in self.p.plate.rows:
#            n+=1
#            m=self.csv[n]
#            location = m[0]+i
#            m.pop(0)
#            self.tmp[readout][location]=m