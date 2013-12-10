from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse

from django.core.paginator import Paginator

from django.views.generic.edit import FormView

from main.tasks import submit_data
from main.forms import UploadFileForm
<<<<<<< HEAD
from main.models import data, project, submission

=======
from main.models import project, submission
from data.models import proj_1 as data
>>>>>>> 190a26f64f080d7861db9b026963a1f43171f45d



# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)

def index(request):
    return render(request, "main/index.html")
#"""request.FILES['datafile'],"""'test','longfei',['1','2']


def datalist(request):
    entry_list = data.objects.all()
    field_list = list()
    for i in data._meta.fields:
        field_list.append(i.name)

    current_page = (request.GET.get('page'))
        
    p = Paginator(entry_list,30)    
    
    if not current_page:
        current_page=1
    
    if int(current_page)+3 >= p.num_pages:
        page_range = range(p.num_pages - 7, p.num_pages)
    else:
        page_range = range(max(1,int(current_page)-3),max(1,int(current_page)-3)+7) 
        

    return render_to_response( "main/data_list.html",{'entry_list': p.page(current_page),
                                                  'field_list': field_list,
                                                  'pages': page_range,
                                                  'last_page':p.num_pages
                                                })

def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        
        if not form.is_valid():
            return render_to_response('main/error.html',{'error_msg':"WTF, you can't even fill a form right? HAAAAAA!"})

        submit_data(form.cleaned_data)
        return HttpResponseRedirect('/main/view/')

#            handle_uploaded_file(request.FILES['file'])
#            return HttpResponseRedirect('/success/url/')

    else:    #a form to upload raw data
        form = UploadFileForm(initial={'library':'test','plates':'1,2','user':'longfei','project':'test'})
        c={'form': form}
        c.update(csrf(request))
    return render_to_response('main/upload.html', c)

