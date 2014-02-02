from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import messages
from main.models import project, score as sc#alias cause name conflict with method
from collections import OrderedDict as od
from process.tasks import process_score
from process.forms import PlatesToUpdate, ScoreForm
from django.db.models import Count
from main.utils import get_platelist,job
import process.readers as readers
from process.tasks import readinback
from process.forms import UploadFileForm
from main.views import view_class
from data.models import project_data_base
from process.models import *
import logging,sys
import simplejson as json


# Create your views here.


class upload(view_class):



    def post(self,request):#handle which one to call based on pointer
        options = {'upload':self.upload,
                   'save':self.save,
                    }
        
        return options[request.POST.get("pointer")](request)

    def upload(self,request):

        datafile=request.FILES[u'files[]']

        #generating json response array
        result = []
        result.append({'name':datafile.name, 
                       'size':datafile.size, 
                       'form':readers.reader(datafile=datafile,proj_id=self.proj.id).parse().render(request=request)#dont's know how to reset file iterator..
                       })
        response_data = json.dumps(result)

        #print >>sys.stderr, 'uploaded', HttpResponse(response_data, content_type='application/json')

        return HttpResponse(response_data, content_type='application/json')


    def save(self,request):

        tmpreader = readers.reader(form=request.POST).create_job()

        readinback.delay(tmpreader.param)

        return redirect('job',tmpreader.param['job_id'])


    def get(self,request):

        form = UploadFileForm(initial={'user':request.user.pk,'project':self.proj.pk})
    
                
        return render(request,'process/upload.html', {'form':form})

 
class mark(view_class):

    def get(self,request):

        form=PlatesToUpdate()
        
        data=self.data

        welltypes=dict(project_data_base.wtchoice)
	del welltypes['X']#no need to set compounds

        proj=self.proj

        plates=self.plates#get list of plates
        x=[]

        if request.method=='POST':
            
            form=PlatesToUpdate(request.POST)

            if form.is_valid():

                platelist=form.cleaned_data['plates'].split(',')
                querybase=data.objects.filter(plate__in=platelist)

                myjob=self.job         
                myjob.create(request,log='select plates: %s to update.'%','.join(platelist))


                if request.POST.get('reset'):
                    pass

                else:

                    for j in ['E','P','N','B']:#this sequence is priority low to high

                        x=request.POST.get(j).split(',')
                        
			if len(x) > 1:    
                            myjob.update(log='updated wells: %(wells)s for welltype %(welltype)s.'%{'welltype':j,'wells':','.join(x)})

                    	querybase.filter(well__in=x).update(set__welltype=j) 

                    querybase.filter(compound__exists=True,welltype__in=['E','P','N']).update(set__welltype='X')#if it has compound reference than you have to make sure
                #querybase.filter(compound__exists=False,welltype='X').update(set__welltype='E')


                messages.success(request,'WellType Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
        
                myjob.complete()

        return render(request,'process/markwell.html',{'proj':proj,'welltypes':welltypes,'plates':plates,'form':form})


class score(view_class):
    def get(self,request):
        form=PlatesToUpdate()

        data=self.data
        proj=self.proj

        entry_list=sc.objects.all()
        
        table_success_list=list()
        for i in proj.score.values('pk'):
            table_success_list.append(i['pk'])

        field_list=['name','description','formular']

        plates=self.plates#get list of plates


        if request.method=='POST':
            form=PlatesToUpdate(request.POST)
            if form.is_valid():

                myjob=self.job
                myjob.create(request,log='Update plates: %s. '%form.cleaned_data['plates'])
                
                if process_score(data.objects.all(),proj,form.cleaned_data['plates'].split(','),self.data):
                    
                    myjob.complete()

                    messages.success(request,'Job has been sent. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
        
        return render(request,'process/score.html',{'plates':plates,
                            'entry_list':entry_list,
                            'field_list':field_list,
                            'form':form,
                            'table_success_list':table_success_list})


