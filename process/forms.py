from django import forms
from main.models import data_base,score

class PlatesToUpdate(forms.Form):
	plates=forms.CharField(initial='',widget=forms.Textarea(attrs={'id':'selector-target','rows':5,'placeholder':'Plates List, like 1,2,3'}))

class ScoreForm(forms.ModelForm):
    class Meta:
        model=score
        fields='name description formular'.split()