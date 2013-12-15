from django.shortcuts import render
from django.core.context_processors import csrf

# Create your views here.

def index(request):
    return render(request,'process/processbase.html',{})
    
def mark(request):
    pass
