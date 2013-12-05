from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.views.generic import FormView, DetailView
from django.core.urlresolvers import reverse

from .tasks import UploadFileForm, readrawdata
from main.models import data, rawDataFile

# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)


def index(request):    
    return render(request,'main/index.html')
#"""request.FILES['datafile'],"""'test','longfei',['1','2']
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result=readrawdata.delay(request.FILES['datafile'],'test','longfei','testlibrary',['1','2'])
            return HttpResponse(result.state)
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


#==============================================================================
## test viewes from QY

## The summary page for all the data generated by one user
def tasks(request):    
    return render(request,'main/tasks.html')

#def submit_table(request):
#    return render(request, 'main/submittable.html')
    
def submit_analysis(request):
    return render(request, 'main/submit2.html')
    
## A class for upload raw datafiles and store at /media/ folder,
    

class upload_raw_datafile(FormView):
    """A class for upload raw datafiles and store at /media/ folder. 
    A more complete version of submit_table_view    
    """

    template_name = 'main/submittable.html'
    form_class = UploadFileForm
    
    def form_valid(self,form):
        raw_datafile = rawDataFile(
            datafile = self.get_form_kwargs().get('files')['datafile'])
        raw_datafile.save()
        self.id = raw_datafile.id
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        """ The reture url for successful upload
        """
        ## to be completed
        return reverse("tasks") 
