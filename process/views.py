from django.shortcuts import render
from django.core.context_processors import csrf
from main.models import project
# Create your views here.

def index(request):
    return render(request,'process/processbase.html',{})
    
def mark(request):
    proj=project.objects.get(pk=request.session['proj_id'])
    
    return render(request,'process/markwell.html',{'proj':proj})
