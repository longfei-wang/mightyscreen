from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,logout
from account.models import RegisterForm

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

def myaccount(request):
    user = request.user
    profile = user.get_profile()
#    raise Exception(user.project_set.values_list())
    return render(request,'account/account.html',{'user':user,'profile':profile})
    
def projselect(request):

    if request.method == 'POST':
        request.session['proj_id']=request.POST.get('proj')
        request.session['proj'] = request.user.project_set.get(pk=request.POST.get('proj')).name
        return render(request,'main/redirect.html',{'message':'Choose'+request.session['proj']+' as your project','dest':'index'})

    projs=request.user.project_set.all()
    args={'projs':projs}
    args.update(csrf(request))    
    return render(request,'account/projselect.html',args)