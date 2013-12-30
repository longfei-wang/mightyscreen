from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from account.models import RegisterForm, ProjectForm
from main.models import project,score,experiment,readout
from django.conf import settings
from django.forms.models import modelform_factory,modelformset_factory
from django.contrib import messages
import main.utils
import json
import os
# Create your views here.
def signin(request):
    form=AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():

            login(request,form.get_user())
            return render(request,'main/redirect.html',{'message':'You are logged in!','dest':'index'})

    args={'form':form}
    args.update(csrf(request))
    return render(request,'account/login.html',args)

def signup(request):
    form=RegisterForm()
    if request.method == 'POST':

        form = RegisterForm(request.POST)
        if form.is_valid():

            form.save()
            return render(request,'main/redirect.html',{'message':'Congrats! You are registered!','dest':'index'})

    #read user agreement
    f=open(settings.BASE_DIR+'/README.md')
    agreement=f.read()
    f.close()

    args={'form':form,'agreement':agreement}
    args.update(csrf(request))

    return render(request,'account/register.html',args)

def logoff(request):
    logout(request)
    return render(request,'main/redirect.html',{'message':'You are logged out!','dest':'index'})

    
#user profile
def profile(request):
    user = request.user
    profile = user.get_profile()
    return render(request,'account/profile.html',{'user':user,'profile':profile})

def jobview(request):
    #proj=request.user.project_set.get(pk=request.session.get('proj_id'))
    field_list=['project','submit_time','submit_by','comments','status','log']
    return render(request,'account/jobs.html',{'field_list':field_list,'proj_id':int(request.session.get('proj_id'))})

#view and manage projects
def projects(request):

    field_list=['name','description','agreement','experiment','plate','replicate','leader']
    args={'field_list':field_list}
    args.update(csrf(request))    
    return render(request,'account/projectlist.html',args)

#to select working project
def projselect(request):

    if request.method == 'GET':
        request.session['proj_id']=request.GET.get('p')
        request.session['proj'] = request.user.project_set.get(pk=request.GET.get('p')).name
        return render(request,'main/redirect.html',{'message':'Choose'+request.session['proj']+' as your project','dest':'index'})

    return render(request,'main/error.html',{})

def projedit(request):
    warning_fields=''
    form=ProjectForm()
    if request.method=='POST':
        if request.POST.get('proj_id'):#decide if create a new project or update one
            form=ProjectForm(request.POST,instance=project.objects.get(pk=request.POST.get('proj_id')))

        else:
            form=ProjectForm(request.POST)
        if form.is_valid():

            if request.POST.get('proj_id') and [i for i in ['experiment','plate','replicate','leader','name'] if i in form.changed_data] and not request.POST.get('warning_fields') :
                warning_fields=', '.join(form.changed_data)#pop the warning message
                return render(request,'account/projectedit.html',{'form':form,
                                                                'proj_id':request.POST.get('proj_id'),
                                                                'warning_fields':warning_fields
                                                                })
            else:
                form.save()
                #not sure if this is safe here. guess so. what if users submit at the same time? has to be queued
                dir=os.path.join(settings.BASE_DIR,'manage.py')
                os.system('python %s schemamigration data --auto'%dir)
                os.system('python %s migrate data'%dir)
                main.utils.flush_transaction()

                return render(request,'main/redirect.html',{'message':'Project Created.','dest':'index'})
        
    proj_id=''    
    if request.method=='GET':
        if request.GET.get('action') != 'new':
            if request.GET.get('p') or request.session.get('proj_id'):
                proj_pid= request.GET.get('p') if request.GET.get('p') else request.session.get('proj_id')
                proj=project.objects.get(pk=proj_pid)
                if request.user in proj.user.all():
                    form=ProjectForm(instance=proj)
                    proj_id=proj.pk

    return render(request,'account/projectedit.html',{'form':form,
                                                    'proj_id':proj_id,
                                                    })

def filternedit(request):
    if request.GET.get('edit'):
        edit=request.GET.get('edit')
        if edit=='score':
            obj=score
        elif edit=='experiment':
            obj=experiment
        elif edit=='readout':
            obj=readout
    else:
        obj=score
        edit='score'

    entry_list=obj.objects.all()
    jsonstring = json.dumps(list(entry_list.values('id','name')))

    formsetobject=modelformset_factory(obj,max_num=1)


    if request.POST.get('ispost'):
        formset=formsetobject(request.POST)
        if formset.is_valid():
                #check if creater of this entry, otherwise no permission!
            formset.save()
            messages.success(request,'Entry Updated!')
    else:
        formset=formsetobject(queryset=obj.objects.filter(
                    pk__in=map(int,request.POST.getlist('selection'))
                    ))

    return render(request,'account/filternedit.html',{'formset':formset,
                                                    'entry_list':entry_list,
                                                    'edit':edit,
                                                    'jsonstring':jsonstring})



