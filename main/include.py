from django import forms
import csv

from main.models import project, data, experiment, readout, fileformat, plate



class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class readrawdata():
    def __init__(self,csvfile,project_name,user_name):
        self.csv = csv.reader(csvfile)
        self.project_name = project_name
        self.user_name=user_name
    
    def parse(self):
        a = project.objects.get(name=self.project_name)
        # a.experiment.readout.all(), a.experiment.readout.count()
        n=''
        for row in self.csv:
            n=n+row[0]+'<br>'
        return n