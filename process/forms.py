from django import forms
from main.models import data_base
class PlatesToUpdate(forms.Form):
	plates=forms.CharField(initial='',widget=forms.Textarea(attrs={'id':'selector-target','rows':5,'placeholder':'Plates List, like 1,2,3'}))
