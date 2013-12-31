from django import forms
import main.readers as readers
from main.models import data_base

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = data_base
        fields=['library_pointer']
    
    #title = forms.CharField(max_length=50)
    project = forms.CharField(widget=forms.HiddenInput)
    user = forms.CharField(widget=forms.HiddenInput)
    library = forms.CharField(required=False,label='Library Name [Optional]',widget=forms.TextInput(attrs={'placeholder':'name of the library if it\'s not in our list'}))
    plates = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'plate list, like 1,2,3'}))
    datafile  = forms.FileField(widget=forms.FileInput())
    comments = forms.CharField(widget=forms.Textarea(),required=False)

