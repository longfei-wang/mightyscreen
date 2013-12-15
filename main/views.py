from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.core.paginator import Paginator
from main.tasks import submit_data
from main.models import UploadFileForm





# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)

def index(request):
    return render(request, "main/index.html")
#"""request.FILES['datafile'],"""'test','longfei',['1','2']


#list view of data in current project. Dynamically import the right model/table for project
def datalist(request):

    if 'proj' in request.session: 
        exec ('from data.models import proj_'+request.session['proj_id']+' as data')
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
            
    
        return render(request, "main/data_list.html",{'entry_list': p.page(current_page),
                                                      'field_list': field_list,
                                                      'pages': page_range,
                                                      'last_page':p.num_pages
                                                    })
    else:
        return render(request,"main/data_list.html",{})




def upload(request):
    if 'proj' in request.session: 
        form = UploadFileForm(initial={'library':'test','plates':'1,2','user':request.user.pk,'project':request.session['proj_id']})
    
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            
            if form.is_valid():
    
                submit_data(form.cleaned_data)
                return render(request,'main/redirect.html',{'message':'Data submitted to queue!','dest':'index'})
    
        #a form to upload raw data
    
        c={'form': form}
        c.update(csrf(request))
    else:
        return render(request,'main/error.html',{'error_msg':'No working project specified!'})
    return render(request,'main/upload.html', c)

