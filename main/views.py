from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib import messages
from django.core import serializers
from main.utils import get_platelist, job
from library.models import compound
from django.views.generic.base import View
from django.conf import settings
from main.models import project, view as views
from mongoengine.queryset import Q
from library.models import *
from data.models import field
import cPickle as pickle
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
                self.project=project.objects.get(pk=settings.DEMO_PROJECT)
            else:
                self.project=project.objects.get(pk=request.session['proj_id'])

        return self.project

    @property
    def data(self):
        """get current project database model"""

        return self.get_data(self.proj.pk)

    def get_data(self,proj_id):
        
        from data.models import project_data_base
        exec('class proj_data_%s(project_data_base):pass;'%str(proj_id))
        exec('data = proj_data_%s'%str(proj_id))
        data.set_proj(project.objects.get(pk=proj_id))
        
        return data


    @property#self.job is the class to submit job
    def job(self):
        """a job object for job submission"""
        if not self.job_obj:
            self.job_obj=job()
        return self.job_obj

    
    def cachekey(self,request):
        """#generate unique key for cache"""
        return request.session._get_or_create_session_key()+str(self.proj.id)

    def post(self,request,*args,**kwargs):
        return self.get(request,*args,**kwargs)



class index(view_class):

    def get(self,request):

        return render(request, "main/index.html")




class table(view_class):
    
    def get(self,request):

        data = self.data
        raise Exception(data.objects.all().to_json())



class datalist(view_class):

    def get(self,request,data=None,rootquery='',field_list=None):
        """list view of data in current project. Dynamically import the right model/table for project"""

        data = self.data if not data else data
        cachekey = self.cachekey(request)
        url = request.path
        field_lock=False #decide if you can customize field or not    
        pre_order='id'
        plates=self.plates
        args=''
        plates_selected=[]
        quoted_fields=['plate','well']#this is for the crappy quote/unquote requirement of mongoengine
        

        #
        #Perform all the Query
        #
        exec('querybase=data.objects'+rootquery)

        

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
            
            args = cache.get('dataview'+cachekey)#if this is just turning pages then use the latest query
            args='' if not args else args

            if request.GET.get('order'):
                pre_order=request.GET.get('order')

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
            
        cache.set('dataview'+cachekey,args,0)

        #
        #Decide fields to display
        #
        if field_list:

            curprojfield_list = field_list

            allfield_list = field_list

            field_lock = True
        
        else:

            curprojfield_list = data.field_list()#field list of current proj

            compoundfield_list = compound.field_list()#field list of compound library


            d=[field('divider','Current Project','')]

            allfield_list=compoundfield_list+d+curprojfield_list


            if request.POST.get('fieldlist'):#for post
                field_list=[i for i in allfield_list if i.name in request.POST.get('fieldlist').split(',')]

            elif cache.get('dataview_field_list'+cachekey) and not request.GET.get('fieldreset'):#for get view, like page, order
            
                field_list=cache.get('dataview_field_list'+cachekey)

            else:#if nothing
                field_list=curprojfield_list

            cache.set('dataview_field_list'+cachekey,field_list,0)    


        #
        #Paginator
        #
        
        current_page = (request.GET.get('page'))

        if not current_page:#current page is the pointer of page
            current_page=1
            

        p = Paginator(entry_list,50) #pages

        page_range = range(int(current_page)-5,int(current_page)+5)
        
        if int(current_page)-5 < 1:
            page_range = range(1,min(10,p.num_pages)+1)
        else:
            if int(current_page)+5 > p.num_pages:
                page_range = range(max(int(p.num_pages)-10,1),p.num_pages+1)
            
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
                                                      'projfield_list':curprojfield_list,
                                                      'proj':self.proj,
                                                      'field_lock':field_lock,
                                                      'url':url,
                                                    })



class save_view(view_class):#save a view
    
    def get(self,request):
        
        response='there is nothing'

        query = cache.get('dataview'+self.cachekey(request)) 
        
        field_list = cache.get('dataview_field_list'+self.cachekey(request))

        if query is not None and field_list:

            

            entry = views(
                query=query,
                field_list=pickle.dumps(field_list),
                user_id=request.user.id,
                proj_id=self.proj.id,
                )
            entry.save()
            response=str(entry.id)

        return HttpResponse(response,mimetype='text')




class get_view(datalist): #retreive views from a view.
    
    def get(self,request,view_id):
        
        view=None

        if view_id:#if there is a saved view then get the view instead
            try:
                view=views.objects.get(id=view_id)
            except:
                pass

        if not view:
            raise Http404
        return super(get_view,self).get(request,self.get_data(view.proj_id),view.query,pickle.loads(str(view.field_list)))



class addtohitlist(view_class):

    def get(self,request):
        
        myjob=self.job

        myjob.create(request)

        if cache.get('dataview'+self.cachekey(request)) is not None:

            args=cache.get('dataview'+self.cachekey(request))

            exec('obj=self.data.objects'+args)

            if request.method=='POST':
                if request.POST.get('hitlist'):
                    
                    hitlist= request.POST.get('hitlist').split(',')

                    obj.filter(id__in=hitlist).update(set__hit=1)
                
                elif request.POST.get('hitlistrm'):
                    
                    hitlistrm= request.POST.get('hitlistrm').split(',')

                    obj.filter(id__in=hitlistrm).update(set__hit=0)

            elif request.GET.get('reset'):

                obj.update(set__hit=0)

            elif request.GET.get('platewell'):

                obj.filter(id=request.GET.get('cid')).update(set__hit=1)
            
            else:
                obj.update(set__hit=1)
        
            messages.success(request,'Hit List Updated')
            myjob.complete()

        else:
            myjob.fail()

        
        return redirect('view')




class export(view_class):
    
    def get(self,request):
        if cache.get('dataview'+self.cachekey(request)) is not None:
            
            args=cache.get('dataview'+self.cachekey(request))

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

                data = obj.to_json()
                
                response = HttpResponse(mimetype='application/json')
                response['Content-Disposition'] = 'attachment;filename="export.json"'
                response.write(data)

                return response
