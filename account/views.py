from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from account.models import RegisterForm

# Create your views here.
def signin(request):
    form=AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():            
            #form.save
            login(request,form.get_user())
            return render_to_response('main/redirect.html',{'message':'You are logged in!','dest':'index'})

    args={'form':form}
    args.update(csrf(request))
    return render_to_response('account/login.html',args)

def signup(request):
    form=RegisterForm()
    
    if request.method == 'POST':

        form = RegisterForm(request.POST)
        if form.is_valid():

            form.save()
            return render_to_response('main/redirect.html',{'message':'Congrats! You are registered!','dest':'index'})


    args={'form':form}
    args.update(csrf(request))

    return render_to_response('account/register.html',args)

def logoff(request):
    logout(request)
    return render_to_response('main/redirect.html',{'message':'You are logged out!','dest':'index'})

def myaccount(request):
    user = request.user
    profile = user.get_profile()
#    raise Exception(user.project_set.values_list())
    return render_to_response('account/account.html',{'user':user,'profile':profile})