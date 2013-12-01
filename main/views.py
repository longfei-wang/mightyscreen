from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.core.context_processors import csrf

from .include import UploadFileForm, readrawdata
from main.models import data

# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)


def index(request):    
    return HttpResponse("Hello, world. You're at the poll index.")

def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            rawdata = readrawdata(request.FILES['file'],'test','longfei')
            
            return HttpResponse(rawdata.parse())
#            handle_uploaded_file(request.FILES['file'])
#            return HttpResponseRedirect('/success/url/')
    else:    #a form to upload raw data
        form = UploadFileForm()
        c={'form': form}
        c.update(csrf(request))
    return render_to_response('main/upload.html', c)


#def gen(request):
#	x=''
#	n=0
#	for r in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']:
#		n=n+1
#		m=0
#		for c in ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24']:
#			m=m+1
#			d = well(
#			plate_type = "384_standard",
#			column = m,
#			row = n,
#			position = r+c,	
#			origin = "topleft",
#			)
#			d.save()
#	return HttpResponse("done")


