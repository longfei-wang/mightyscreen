from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from main.models import project,experiment,readout,score,plate
# Create your models here.


class user_profile (models.Model):
    user = models.OneToOneField(User)
    affiliation = models.CharField(max_length=100)
    position = models.CharField(max_length=50)

class RegisterForm(UserCreationForm):
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


class ProjectForm(forms.ModelForm):
    class Meta:
        model=project
        fields=['name','description','agreement','experiment','plate','replicate','score','leader','user']