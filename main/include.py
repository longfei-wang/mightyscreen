from django import forms
import csv

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class readrawdata():
    
    def __init__(self,csvfile):
        self.csv = csv.reader(csvfile)
    
    def parse(self):
        n=''
        for row in self.csv:
            n=n+row[0]+'<br>'
        return n