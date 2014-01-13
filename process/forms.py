from django import forms
from main.models import score

class PlatesToUpdate(forms.Form):
	plates=forms.CharField(initial='',widget=forms.Textarea(attrs={'id':'selector-target','rows':5,'placeholder':'Plates List, like 1,2,3'}))

class ScoreForm(forms.ModelForm):
    class Meta:
        model=score
        fields='name description formular'.split()


class UploadFileForm(forms.Form):
    
    #title = forms.CharField(max_length=50)
    project = forms.CharField(widget=forms.HiddenInput)
    user = forms.CharField(widget=forms.HiddenInput)
    library = forms.CharField(required=False,label='Library Name [Optional]',widget=forms.TextInput(attrs={'placeholder':'name of the library if it\'s not in our list'}))
    plates = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'plate list, like 1,2,3'}))
    datafile  = forms.FileField(widget=forms.FileInput())
    comments = forms.CharField(widget=forms.Textarea(),required=False)

