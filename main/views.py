from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from main.tasks import submit_data
from main.models import UploadFileForm
from django.core.cache import cache





# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)

def index(request):
    return render(request, "main/index.html")
#"""request.FILES['datafile'],"""'test','longfei',['1','2']



def datalist(request):
    """list view of data in current project. Dynamically import the right model/table for project"""

    if not 'proj' in request.session:
        return render(request,"main/error.html",{'error_msg':"No project specified!"})
        
        
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')
    
        
    
    if request.POST.get('querytext'):

        query='Q('+request.POST.get('field')+'__'+request.POST.get('sign')+' = "'+request.POST.get('querytext')+'")'

        if request.POST.get('querytext2') and request.POST.get('joint'):

            query+=request.POST.get('joint')+'Q('+request.POST.get('field2')+'__'+request.POST.get('sign2')+' = "'+request.POST.get('querytext2')+'")'
        #raise Exception(query)
        exec('entry_list = data.objects.filter('+query+')')
        
    else:
        #if this is just turning pages then use the latest query
        if cache.get('dataview') and request.method == 'GET':
            entry_list = cache.get('dataview')

            if request.GET.get('order'):
                
                query='entry_list.order_by("'+request.GET.get('order')+'")'
                #raise Exception(query)
                exec("entry_list = "+query)
                
        else:
            entry_list = data.objects.all()


    cache.set('dataview',entry_list)





    field_list = list()
    for i in data._meta.fields:
        field_list.append(i.name)

    current_page = (request.GET.get('page'))

    if not current_page:
        current_page=1
        

    p = Paginator(entry_list,100)    

    page_range = range(int(current_page)-5,int(current_page)+5)
    
    if int(current_page)-5 < 1:
        page_range = range(1,min(p.num_pages,11))
    if int(current_page)+5 > p.num_pages:
        page_range = range(max(1,p.num_pages-10),p.num_pages)
  
        

    return render(request, "main/data_list.html",{'entry_list': p.page(current_page),
                                                  'field_list': field_list,
                                                  'pages': page_range,
                                                  'last_page':p.num_pages,
                                                  'curr_page':int(current_page),
                                                  'next_page':min(p.num_pages,int(current_page)+1),
                                                  'prev_page':max(1,int(current_page)-1),
                                                })




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

