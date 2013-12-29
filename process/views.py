from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import messages
from main.models import project, data_base, score
from collections import OrderedDict as od
from process.tasks import process_score
from process.forms import PlatesToUpdate, ScoreForm
from django.db.models import Count
#from main.utils import get_platelist
# Create your views here.
    
def mark(request):
    form=PlatesToUpdate()
    if not 'proj' in request.session:
            return render(request,"main/error.html",{'error_msg':"No project specified!"})
    
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')
    welltypes=od(sorted(dict(data_base.schoice).items()))
    proj=project.objects.get(pk=request.session['proj_id'])

    #get list of plates
    plates=list()
    for i in list(data.objects.values('plate').annotate(x=Count('plate'))):
            plates.append(i['plate'])
    plates=sorted(plates)

    if request.method=='POST':
            form=PlatesToUpdate(request.POST)
            if form.is_valid():
                    #raise Exception(form.cleaned_data)
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

    entry_list=proj.score.all()
    field_list=['name','description','formular']

    #get list of plates
    plates=list()
    for i in list(data.objects.values('plate').annotate(x=Count('plate'))):
            plates.append(i['plate'])
    plates=sorted(plates)


    if request.method=='POST':
            form=PlatesToUpdate(request.POST)
            if form.is_valid():
                    if process_score(data.objects.all(),proj,form.cleaned_data['plates'].split(',')):
                            messages.success(request,'Job has been sent. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
    return render(request,'process/score.html',{'plates':plates,
            'entry_list':entry_list,
            'field_list':field_list,
            'form':form})


def editscore(request):
    form=ScoreForm()
    score_id=''
    if request.method=='POST':
        if request.POST.get('score_id'):#decide if create a new score or update one
            form=ScoreForm(request.POST,instance=project.objects.get(pk=request.POST.get('score_id')))

        else:
            form=ScoreForm(request.POST)
        if form.is_valid():
            form.save()

            return render(request,'main/redirect.html',{'message':'Score Created.','dest':'index'})
    if request.method=='GET':
        if request.GET.get('s'):
            score=score.objects.get(pk=request.GET.get('s'))
            form=ProjectForm(instance=score)
            score_id=score.pk

    return render(request,'account/projectedit.html',{'form':form,'score_id':score_id})