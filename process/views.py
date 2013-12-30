from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import messages
from main.models import project, data_base, score as sc#alias cause name conflict with method
from collections import OrderedDict as od
from process.tasks import process_score
from process.forms import PlatesToUpdate, ScoreForm
from django.db.models import Count
from main.utils import get_platelist
#from main.utils import get_platelist
# Create your views here.
    
def mark(request):
    form=PlatesToUpdate()
    if not 'proj' in request.session:
            return render(request,"main/error.html",{'error_msg':"No project specified!"})
    
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')
    welltypes=od(sorted(dict(data_base.schoice).items()))
    proj=project.objects.get(pk=request.session['proj_id'])

    plates=get_platelist(model=data)#get list of plates

    if request.method=='POST':
            form=PlatesToUpdate(request.POST)
            if form.is_valid():
                    for j in welltypes.keys():
                            if request.POST.get(j):
                                    x=request.POST.get(j)
                                    data.objects.filter(plate__in=form.cleaned_data['plates'].split(','),well__in=x.split(',')).update(welltype=j)
                    messages.success(request,'WellType Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
    
    return render(request,'process/markwell.html',{'proj':proj,'welltypes':welltypes,'plates':plates,'form':form})

def score(request):
    form=PlatesToUpdate()

    if not 'proj' in request.session:
            return render(request,"main/error.html",{'error_msg':"No project specified!"})
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')        
    proj=project.objects.get(pk=request.session['proj_id'])

    entry_list=sc.objects.all()
    
    table_success_list=list()
    for i in proj.score.values('pk'):
        table_success_list.append(i['pk'])

    field_list=['name','description','formular']

    plates=get_platelist(model=data)#get list of plates


    if request.method=='POST':
            form=PlatesToUpdate(request.POST)
            if form.is_valid():
                    if process_score(data.objects.all(),proj,form.cleaned_data['plates'].split(',')):
                            messages.success(request,'Job has been sent. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
    return render(request,'process/score.html',{'plates':plates,
            'entry_list':entry_list,
            'field_list':field_list,
            'form':form,
            'table_success_list':table_success_list})
