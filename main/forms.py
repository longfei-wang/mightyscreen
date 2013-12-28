from django import forms
import main.readers as readers
from main.tasks import queue


class UploadFileForm(forms.Form):
    def submit_data(self):
        #define the submission method here.
        d = readers.Envision_Grid_Reader(self.cleaned_data)
        if d.parse():
        	#then parse_data in background
			queue(d,"save()")
			return 'submitted'
    #title = forms.CharField(max_length=50)
    project = forms.CharField(widget=forms.HiddenInput)
    user = forms.CharField(widget=forms.HiddenInput)
    library = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Library Name'}))
    plates = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Plates List, like 1,2,3 '}))
    datafile  = forms.FileField(widget=forms.FileInput())
    comments = forms.CharField(widget=forms.Textarea(),required=False)


