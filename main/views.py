from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib import messages
from django.core import serializers
from main.utils import get_platelist, job
from library.models import compound
from sabridge.base import Bridge
from django.views.generic.base import View
from main.models import project
from mongoengine.queryset import Q
import csv
import time
# Create your views here.


class field_list_class():#template variable containter for field_list
    def __init__(self,name,verbose_name):
        self.name=name
        self.verbose_name=verbose_name
    def __eq__(self,other):
        return self.name==other.name
    def __ne__(self,other):
        return not self.__eq__(other)


class view_class(View):#the base view class for all
    
    job_obj=None
    platelist=[]
    data_model=None
    project=None

    @property
    def plates(self):
        """retreive a list of plates in current project database"""
        if not self.platelist:
            plates=list()    
            result=self.data._get_collection().aggregate({"$group":{"_id":"$plate"}})['result']
            for i in result:
                plates.append(i['_id'])

            self.platelist=plates

        return self.platelist

    @property
    def proj(self):
        request=self.request
        """get current project"""
        if not self.project:
            if not 'proj' in request.session:
                self.project=project.objects.get(pk=1)
            else:
                self.project=project.objects.get(pk=request.session['proj_id'])

        return self.project

    @property
    def data(self):
        """get current project database model"""

        from data.models import project_data_base
        exec('class proj_data_%s(project_data_base):pass;'%str(self.proj.pk))
        exec('data = proj_data_%s'%str(self.proj.pk))
        data.set_proj(self.proj)
        return data

    @property#self.job is the class to submit job
    def job(self):
        """a job object for job submission"""
        if not self.job_obj:
            self.job_obj=job()
        return self.job_obj

    def get(self,request):
        #this can be overwritten
        return self.c(request)
    
    def post(self,request):
        #this can be overwritten
        return self.c(request)

    def c(self,request):#combine get and post for easier migration, you can overwrite get or post if u want
        pass












class index(view_class):

    def c(self,request):

        return render(request, "main/index.html")

def benchmark(request):
    """compare native django orm and django-sabridge + SQLAlchemy"""

    if not 'proj' in request.session:
        exec ('from data.models import proj_1 as data')      
        
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')

    start=time.clock()
    tmp=compound.objects.all()
    n=0
    for i in tmp:
        n+=1
    elapsed = (time.clock() - start)

    a= elapsed

    bridge = Bridge()
    c=bridge[compound]
    d=bridge[data]

    start=time.clock()

    result=c.select().execute()

    m=0
    for i in result:
        
        m+=1
    elapsed = (time.clock() - start)
    
    b=elapsed

    return HttpResponse(str(a)+','+str(n)+','+str(b)+','+str(m))










class datalist(view_class):

    def c(self,request):
        """list view of data in current project. Dynamically import the right model/table for project"""

        pre_order='id'
        plates=self.plates
        data=self.data
        args=''
        plates_selected=[]
        quoted_fields=['plate','well']#this is for the crappy quote/unquote requirement of mongoengine
        #
        #Perform all the Query
        #

        querybase=data.objects.all()

        
        if request.method=='POST':
 
            if request.POST.get('plates'):
                plates_selected=request.POST.get('plates').split(',')#plates_selected is a pass-through variable
                args+='.filter(plate__in=%s)'%plates_selected

            if request.POST.get('querytext'):#first query bar
                quote = '"' if request.POST.get('field') in quoted_fields else ''
                query='Q('+request.POST.get('field')+'__'+request.POST.get('sign')+' = '+quote+request.POST.get('querytext')+quote+')'

                if request.POST.get('querytext2') and request.POST.get('joint'):#second query bar
                    quote = '"' if request.POST.get('field2') in quoted_fields else ''
                    query+=request.POST.get('joint')+'Q('+request.POST.get('field2')+'__'+request.POST.get('sign2')+' = '+quote+request.POST.get('querytext2')+quote+')'
            
                args+='.filter(%s)'%query
            
        else:
            
            args = cache.get('dataview'+str(self.proj.pk))#if this is just turning pages then use the latest query
            args='' if not args else args

            if request.GET.get('order'):
                pre_order=request.GET.get('order')
                #intense query sting cause we need to put null entries last..
                args+='.order_by("%s")'%pre_order
                

            elif request.GET.get('filter'):

                if request.GET.get('filter') == 'reset':
                
                    args=''
                
                else:
                    args='.filter(%s__gt=0)'%request.GET.get('filter')

        try:
            exec ('entry_list=querybase'+args)
        except:
            args=''
            entry_list=querybase
            messages.warning(request,'A Internal Error Occured. Your list will be reset.')
            
        cache.set('dataview'+str(self.proj.pk),args,3600)

        #
        #Decide fields to display
        #

        curprojfield_list = data.field_list()
        compoundfield_list=list()

        # for i in compound._meta.fields:
        #     if i.name not in compound.hidden_fields:
        #         i.name='compound_pointer__'+i.name if 'compound_pointer__' not in i.name else i.name#have to prefix the name to make query possible. related field name
        #         compoundfield_list.append(field_list_class(i.name,i.verbose_name))


        d=field_list_class('divider','Current Project')

        allfield_list=curprojfield_list

        if request.POST.get('fieldlist'):#for post
            field_list=[i for i in allfield_list if i.name in request.POST.get('fieldlist').split(',')]

        elif cache.get('dataview_field_list'+str(self.proj.pk)) and not request.GET.get('fieldreset'):#for get view, like page, order
        
            field_list=cache.get('dataview_field_list'+str(self.proj.pk))

        else:#if nothing
            field_list=curprojfield_list


        cache.set('dataview_field_list'+str(self.proj.pk),field_list,3600)    


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
                                                      'proj':self.proj
                                                    })




class addtohitlist(view_class):
    
    def c(self,request):
        
        myjob=self.job

        myjob.create(request)

        if cache.get('dataview'+str(self.proj.pk)) is not None:

            args=cache.get('dataview'+str(self.proj.pk))

            exec('obj=self.data.objects'+args)

            if request.method=='POST':
                if request.POST.get('hitlist'):
                    
                    hitlist= request.POST.get('hitlist').split(',')

                    obj.filter(platewell__in=hitlist).update(set__hit=1)
                
                elif request.POST.get('hitlistrm'):
                    
                    hitlistrm= request.POST.get('hitlistrm').split(',')

                    obj.filter(platewell__in=hitlistrm).update(set__hit=0)

            elif request.GET.get('reset'):

                obj.update(set__hit=0)

            elif request.GET.get('platewell'):

                obj.filter(platewell=request.GET.get('platewell')).update(set__hit=1)
            
            else:
                obj.update(set__hit=1)
        
            messages.success(request,'Hit List Updated')
            myjob.complete()

        else:
            myjob.fail()

        
        return redirect('view')


class export(view_class):
    def c(self,request):
        if cache.get('dataview'+str(self.proj.pk)) is not None:
            
            args=cache.get('dataview'+str(self.proj.pk))

            exec('obj=self.data.objects'+args)
            
            field_list=self.data.field_list()

            if request.GET.get('format')=='csv':

                response = HttpResponse(mimetype='text/csv')

                response['Content-Disposition'] = 'attachment;filename="export.csv"'

                writer = csv.writer(response)

                header_row=True
                header=[]
                
                for i in field_list:
                    header.append(i.verbose_name)
                writer.writerow(header)

                for i in obj:
                    values=[]
                    for j in field_list:
                        values.append(getattr(i,j.name))

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