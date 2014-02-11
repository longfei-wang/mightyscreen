from django import forms
from userena.forms import SignupForm
from accounts.models import *


class RegisterForm(SignupForm):#a extension model form based on usercreateform

    first_name=forms.CharField(max_length=30)
    last_name=forms.CharField(max_length=30)
    affiliation = forms.CharField(max_length=100)
    position = forms.CharField(max_length=50)       
    
    def __init__(self, *args, **kw):
        """

        A bit of hackery to get the first name and last name at the top of the
        form instead at the end.

        """
        super(RegisterForm, self).__init__(*args, **kw)
        # Put the first and last name at the top
        new_order = self.fields.keyOrder[:-4]
        new_order.insert(0, 'first_name')
        new_order.insert(1, 'last_name')
        new_order.insert(2, 'affiliation')
        new_order.insert(3, 'position')
        self.fields.keyOrder = new_order


    def save(self):
        """
        Override the save method to save the first and last name to the user
        field.

        """
        # First save the parent form and get the user.
        new_user = super(RegisterForm, self).save()

        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()

        profile,created = usersprofile.objects.get_or_create(user=new_user)
	profile.affiliation=self.cleaned_data['affiliation']
	profile.position=self.cleaned_data['position']
	profile.save()

        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user
