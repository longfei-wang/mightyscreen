from django.shortcuts import render,redirect
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
from main.utils import get_platelist, job
import main.readers as readers
from main.tasks import queue
from library.models import compound
import csv
from itertools import chain
# Create your views here.

#def handle_uploaded_file(f):
#    with open('some/file/name.txt', 'wb+') as destination:
#        for chunk in f.chunks():
#            destination.write(chunk)

class field_list_class():#template variable containter for field_list
    def __init__(self,name,verbose_name):
        self.name=name
        self.verbose_name=verbose_name
    def __eq__(self,other):
        return self.name==other.name
    def __ne__(self,other):
        return not self.__eq__(other)


def index(request):

    return render(request, "main/index.html")


def datalist(request):
    """list view of data in current project. Dynamically import the right model/table for project"""

    pre_order='id'
    plates_selected=list()

    if not 'proj' in request.session:
        return render(request,"main/error.html",{'error_msg':"No project specified!"})      
        
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')
    
    plates=get_platelist(model=data)#get array of plates



    #
    #Perform all the Query
    #

    querybase=data.objects.all()

    if request.POST.get('plates'):
        plates_selected=request.POST.get('plates').split(',')#plates_selected is a pass-through variable
        querybase=querybase.filter(plate__in=plates_selected)
    
    querybase.order_by('pk')        
    
    if request.method=='POST':

        if request.POST.get('querytext'):#first query box

            query='Q('+request.POST.get('field')+'__'+request.POST.get('sign')+' = "'+request.POST.get('querytext')+'")'

            if request.POST.get('querytext2') and request.POST.get('joint'):#second querybox

                query+=request.POST.get('joint')+'Q('+request.POST.get('field2')+'__'+request.POST.get('sign2')+' = "'+request.POST.get('querytext2')+'")'
        
            #raise Exception(query)
            exec('entry_list = querybase.filter('+query+')')

        else:#when you hit update with no querytext

            entry_list = querybase
        
    else:
        
        try:#wierd error association cache, have no idea how to fix this. So just if error occur, reset cache...
            entry_list = cache.get('dataview'+request.session['proj_id'])#if this is just turning pages then use the latest query
        
        except:
            entry_list = None
            messages.error(request,"A Internal Error Occured. And your veiw will be reset.")

        entry_list = entry_list if entry_list else querybase        

        if request.GET.get('order'):
            pre_order=request.GET.get('order')
            #intense query sting cause we need to put null entries last..
            query='entry_list.order_by("%s")'%pre_order
            
            
            exec("entry_list = "+query)


    cache.set('dataview'+request.session['proj_id'],entry_list,30)


    #
    #Decide fields to display
    #
    
    curprojfield_list = [field_list_class(i.name,i.verbose_name) for i in data._meta.fields if i.name not in data.hidden_fields]#get all field we can display

    compoundfield_list=list()

    for i in compound._meta.fields:
        if i.name not in compound.hidden_fields:
            i.name='compound_pointer__'+i.name if 'compound_pointer__' not in i.name else i.name#have to prefix the name to make query possible. related field name
            compoundfield_list.append(field_list_class(i.name,i.verbose_name))


    d=field_list_class('divider','Current Project')

    allfield_list=compoundfield_list+[d]+curprojfield_list

    if request.POST.get('fieldlist'):#for post

        field_list=[field_list_class(i.name,i.verbose_name) for i in allfield_list if i.name in request.POST.get('fieldlist').split(',')]

    elif cache.get('dataview_field_list'+request.session['proj_id']) and not request.GET.get('fieldreset'):#for get view, like page, order
    
        field_list=cache.get('dataview_field_list'+request.session['proj_id'])

    else:#if nothing
        field_list=curprojfield_list


    cache.set('dataview_field_list'+request.session['proj_id'],field_list,3600)    


    #
    #Paginator
    #
    
    current_page = (request.GET.get('page'))

    if not current_page:#current page is the pointer of page
        current_page=1
        

    p = Paginator(entry_list,100) #pages

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
                                                  'allfield_list':allfield_list,
                                                })


def upload(request):

    if 'proj' in request.session: 
        form = UploadFileForm(initial={'user':request.user.pk,'project':request.session['proj_id']})
    
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                reader = readers.Envision_Grid_Reader(form.cleaned_data)#if fileformat is other than Envision need to call other reader
                reader.parse()
                queue(reader,'save()')#then parse_data in background
                    
                return render(request,'main/redirect.html',{'message':'Data submitted to queue!','dest':'index'})
                
    else:
        return render(request,'main/error.html',{'error_msg':'No working project specified!'})
    return render(request,'main/upload.html', {'form':form})


def addtohitlist(request):

    myjob=job()

    myjob.create(request)

    if cache.get('dataview'+request.session['proj_id']):
        
        obj=cache.get('dataview'+request.session['proj_id'])

        if request.method=='POST':

            hitlist= request.POST.get('hitlist').split(',')

            obj.filter(platewell__in=hitlist).update(ishit=1)
        
        elif request.GET.get('reset'):

            obj.update(ishit=0)

        elif request.GET.get('platewell'):

            obj.filter(platewell=request.GET.get('platewell')).update(ishit=1)
        
        else:

            obj.update(ishit=1)
    else:
        myjob.fail()

        messages.success(request,'Hit List Updated')
        myjob.complete()
        
    return redirect('view')


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