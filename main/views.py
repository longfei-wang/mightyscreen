from django.shortcuts import render
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q,Count
from django.core.paginator import Paginator
from main.forms import UploadFileForm
from django.core.cache import cache
from django.contrib import messages
from django.core import serializers
import csv
# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)

def index(request):
    return render(request, "main/index.html")


def datalist(request):
    """list view of data in current project. Dynamically import the right model/table for project"""

    pre_order='id'
    plates_selected=list()

    if not 'proj' in request.session:
        return render(request,"main/error.html",{'error_msg':"No project specified!"})
        
        
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')
    
    plates=list()
    for i in list(data.objects.values('plate').annotate(x=Count('plate'))):
        plates.append(i['plate'])
    plates=sorted(plates)


    if request.POST.get('plates'):
        plates_selected=request.POST.get('plates').split(',')
        querybase=data.objects.filter(plate__in=plates_selected).order_by('pk')

    else:
        querybase=data.objects.order_by('pk')


    if request.POST.get('querytext'):#first query box

        query='Q('+request.POST.get('field')+'__'+request.POST.get('sign')+' = "'+request.POST.get('querytext')+'")'

        if request.POST.get('querytext2') and request.POST.get('joint'):#second querybox

            query+=request.POST.get('joint')+'Q('+request.POST.get('field2')+'__'+request.POST.get('sign2')+' = "'+request.POST.get('querytext2')+'")'
        #raise Exception(query)
        exec('entry_list = querybase.filter('+query+')')
        
    else:
        #if this is just turning pages then use the latest query
        if cache.get('dataview'+request.session['proj_id']) and request.method == 'GET':
            entry_list = cache.get('dataview'+request.session['proj_id'])

            if request.GET.get('order'):
                pre_order=request.GET.get('order')
                #intense query sting cause we need to put null entries last..
                query='entry_list.order_by("%s")'%pre_order

                #raise Exception(query)
                exec("entry_list = "+query)
                
        else:
            entry_list = querybase


    cache.set('dataview'+request.session['proj_id'],entry_list)


    field_list = list()
    for i in data._meta.fields:
        if i.name not in data.hidden_field:
            field_list.append(i.name)
    current_page = (request.GET.get('page'))

    if not current_page:
        current_page=1
        

    p = Paginator(entry_list,100)    

    page_range = range(int(current_page)-5,int(current_page)+5)
    
    if int(current_page)-5 < 1:
        page_range = range(1,min(int(current_page)+10,p.num_pages)+1)
    else:
        if int(current_page)+5 > p.num_pages:
            page_range = range(max(int(current_page)-10,1),p.num_pages+1)
        
    pb_attr='disabled' if len(page_range) < 2 else ''

    return render(request, "main/data_list.html",{'entry_list': p.page(current_page),
                                                  'num_entries':entry_list.count(),
                                                  'field_list': field_list,
                                                  'pages': page_range,
                                                  'last_page':p.num_pages,
                                                  'curr_page':int(current_page),
                                                  'next_page':min(p.num_pages,int(current_page)+1),
                                                  'prev_page':max(1,int(current_page)-1),
                                                  'pbutton_attr':pb_attr,
                                                  'pre_order':pre_order,
                                                  'plates':plates,
                                                  'plates_selected':plates_selected,
                                                })




def upload(request):
    if 'proj' in request.session: 
        form = UploadFileForm(initial={'user':request.user.pk,'project':request.session['proj_id']})
    
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            
            if form.is_valid():
    
                form.submit_data()
                return render(request,'main/redirect.html',{'message':'Data submitted to queue!','dest':'index'})
    
        #a form to upload raw data
    
        c={'form': form}
        c.update(csrf(request))
    else:
        return render(request,'main/error.html',{'error_msg':'No working project specified!'})
    return render(request,'main/upload.html', c)

def export(request):


    if cache.get('dataview'+request.session['proj_id']):
        
        obj=cache.get('dataview'+request.session['proj_id'])

        if request.GET.get('format')=='csv':

            response = HttpResponse(mimetype='text/csv')

            response['Content-Disposition'] = 'attachment;filename="export.csv"'

            writer = csv.writer(response)

            header_row=True
            header=[]
            for i in obj.values():
                values=[]
                for key in i:
                    if header_row:
                        header.append(key)
                    values.append(i[key])
                if header_row:
                    writer.writerow(header)
                    header_row=False
                writer.writerow(values)

            return response

        elif request.GET.get('format')=='xml':

            data = serializers.serialize("xml", obj)

            response = HttpResponse(mimetype='application/xml')
            response['Content-Disposition'] = 'attachment;filename="export.xml"'
            response.write(data)

            return response

        elif  request.GET.get('format')=='json':

            data = serializers.serialize("json", obj)
            
            response = HttpResponse(mimetype='application/json')
            response['Content-Disposition'] = 'attachment;filename="export.json"'
            response.write(data)

            return response