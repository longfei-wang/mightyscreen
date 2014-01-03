from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from main.models import project,experiment,readout,score,plate
# Create your models here.


class user_profile (models.Model):
    def __unicode__(self):
        return self.user.username
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100)
    position = models.CharField(max_length=50)

class RegisterForm(UserCreationForm):#a extension model form based on usercreateform
    first_name=forms.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    email=forms.EmailField()
    affiliation = forms.CharField(max_length=100)
    position = forms.CharField(max_length=50)       
    
    class Meta:
        model = User
        fields = ("username","first_name","last_name","email","affiliation","position","password1", "password2")

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create User and UserProfile without database save")
        user = super(RegisterForm, self).save(commit=True)
        profile = user_profile(user=user, affiliation=self.cleaned_data['affiliation'], 
            position=self.cleaned_data['position'])
        profile.save()
        return user, user_profile


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
