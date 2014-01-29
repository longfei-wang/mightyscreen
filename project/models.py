from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from main.models import project,experiment,readout,score,plate
# Create your models here.






class ProjectForm(forms.ModelForm):#a model form for project
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            if instance.pk:#make sure when edit a existing entry you don't mess around with certain fields
                for i in 'name replicate leader experiment plate leader'.split():
                        self.fields[i].widget.attrs['readonly'] = True
                    # for i in 'experiment plate leader'.split():#select box also need disabled
                    #     self.fields[i].widget.attrs['disabled'] = 'disabled'
            else:
                self.fields['leader'].widget.attrs['readonly'] = True
                
    class Meta:
        model=project
        fields='name description agreement experiment plate replicate score leader user'.split()
