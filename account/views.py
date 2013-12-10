from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
def login(request):
    return render_to_response('account/login.html','')

def myaccount(request):
    pass