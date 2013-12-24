from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from account.models import RegisterForm, ProjectForm
from main.models import project
import os
# Create your views here.
def signin(request):
    form=AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():            
            #form.save
            login(request,form.get_user())
            return render(request,'main/redirect.html',{'message':'You are logged in!','dest':'index'})

    args={'form':form}
    args.update(csrf(request))
    return render(request,'account/login.html',args)

def signup(request):
    form=RegisterForm()
    #for i in form:
        # raise Exception(i.__str__())
    if request.method == 'POST':

        form = RegisterForm(request.POST)
        if form.is_valid():

            form.save()
            return render(request,'main/redirect.html',{'message':'Congrats! You are registered!','dest':'index'})


    args={'form':form}
    args.update(csrf(request))

    return render(request,'account/register.html',args)

def logoff(request):
    logout(request)
    return render(request,'main/redirect.html',{'message':'You are logged out!','dest':'index'})

    
#user profile
def profile(request):
    #raise Exception(dir(request))
    user = request.user
    profile = user.get_profile()
#    raise Exception(user.project_set.values_list())
    return render(request,'account/profile.html',{'user':user,'profile':profile})

#view and manage projects
def projects(request):
    if request.GET.get('p'):
        proj=request.user.project_set.get(pk=request.GET.get('p'))
       # raise Exception(dir(proj.submission_set.get(pk=1).submission_plate_list_set))
        field_list=['project','submit_time','submit_by','comments','status','log']
        return render(request,'account/projectdetail.html',{'proj':proj,'field_list':field_list})
        

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

    form=ProjectForm()
    proj_id=''
    if request.method=='POST':
        if request.POST.get('proj_id'):#decide if create a new project or update one
            form=ProjectForm(request.POST,instance=project.objects.get(pk=request.POST.get('proj_id')))

        else:
            form=ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            #not sure if this is safe here. guess so
            dir=os.path.dirname(os.path.dirname(__file__))
            os.system('python %s\manage.py schemamigration data --auto'%dir)
            os.system('python %s\manage.py migrate data'%dir)

            return render(request,'main/redirect.html',{'message':'Project Created.','dest':'index'})
    if request.method=='GET':
        if request.GET.get('p'):
            proj=project.objects.get(pk=request.GET.get('p'))
            if request.user in proj.user.all():
                form=ProjectForm(instance=proj)
                proj_id=proj.pk

    return render(request,'account/projectedit.html',{'form':form,'proj_id':proj_id})