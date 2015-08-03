from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from accounts.models import RegisterForm
from django.conf import settings

# Create your views here.

def register(request):
    form=RegisterForm()
    if request.method == 'POST':

        form = RegisterForm(request.POST)
        if form.is_valid():

            form.save()
            return render(request,'redirect.html',{'message':'Congrats! You are registered!','dest':'login'})

    #read user agreement
    f=open(settings.BASE_DIR+'/README.md')
    agreement=f.read()
    f.close()

    args={'form':form,'agreement':agreement}
    args.update(csrf(request))

    return render(request,'accounts/register.html',args)

    
#user profile
def profile(request):
    user = request.user
    return render(request,'accounts/profile.html',{'user':user})
