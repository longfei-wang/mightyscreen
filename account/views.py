from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def login(request):
    return render_to_response('account/login.html','')

def register(request):
    a=User()
    #raise Exception(dir(a.userprofile))
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            #form.save
            return render_to_response('main/redirect.html',{'message':'Congrats! You are registered!','dest':'index'})
    args={'form':UserCreationForm()}
    args.update(csrf(request))
    return render_to_response('account/register.html',args)

def myaccount(request):
    pass