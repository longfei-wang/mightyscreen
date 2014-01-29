from django.shortcuts import render,redirect
from django.core.context_processors import csrf
from django.http import HttpResponse,Http404
from project.models import ProjectForm
from main.models import project,score,experiment,readout
from django.conf import settings
from django.forms.models import modelform_factory,modelformset_factory
from django.contrib import messages
from django.forms import Select
from django.core.cache import cache
from main.views import view_class
import main.utils
import simplejson as json
import os
# Create your views here.

class joblist(view_class):

    def get(self,request):
        proj_id=self.proj.id

        field_list=['project','jobtype','submit_time','submit_by','comments','status','log']
        return render(request,'project/joblist.html',{'field_list':field_list,'proj_id':int(proj_id)})


class job(view_class): #a view that display all the running jobs

    def get(self,request,job_id):
        if not job_id:
            raise Http404

        return render(request,'project/job.html',{'job':self.job.get(job_id)})




#view and manage projects
class projects(view_class):

    def get(self,request):
        field_list=['name','description','agreement','experiment','plate','replicate','leader']
        return render(request,'project/projectlist.html',{'field_list':field_list})

#to select working project
class projselect(view_class):
    def get(self,request):

        if request.method == 'GET':
            request.session['proj_id']=request.GET.get('p')
            request.session['proj'] = request.user.project_set.get(pk=request.GET.get('p')).name
            return render(request,'main/redirect.html',{'message':'Choose'+request.session['proj']+' as your project','dest':'index'})

        return render(request,'main/error.html',{})

class projedit(view_class):

    def get(self,request):

        warning_fields=''
        form=ProjectForm()
        proj_id=''

        if request.method=='POST':#posted form
            if request.POST.get('proj_id'):#decide if create a new project or update one
                form=ProjectForm(request.POST,instance=project.objects.get(pk=request.POST.get('proj_id')))

            else:
                form=ProjectForm(request.POST)
            if form.is_valid():

                if request.POST.get('proj_id') and [i for i in ['experiment','plate','replicate','leader','name'] if i in form.changed_data] and not request.POST.get('warning_fields') :
                    warning_fields=', '.join(form.changed_data)#pop the warning message
                    return render(request,'project/projectedit.html',{'form':form,
                                                                    'proj_id':request.POST.get('proj_id'),
                                                                    'warning_fields':warning_fields
                                                                    })
                else:
                    form.save()
                    # dir=os.path.join(settings.BASE_DIR,'reloadmodels.py')
                    # os.system('python %s'%dir)                
                    #not sure if this is safe here. guess so. what if users submit at the same time? has to be queued

                    return render(request,'main/redirect.html',{'message':'Project Created.','dest':'index'})
            
            return render(request,'project/projectedit.html',{'form':form,'proj_id':proj_id})
            

        elif (request.GET.get('p') or request.session.get('proj_id')) and request.GET.get('action') != 'new':#edit project
            proj_pid= request.GET.get('p') if request.GET.get('p') else request.session.get('proj_id')
            proj=project.objects.get(pk=proj_pid)
            if request.user in proj.user.all():
                form=ProjectForm(instance=proj)
                proj_id=proj.pk

        else:#create a new project
            form=ProjectForm(initial={'leader':request.user,'user':[request.user]})

        return render(request,'project/projectedit.html',{'form':form,'proj_id':proj_id})

class filternedit(view_class):
    def get(self,request):


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

        formsetobject=modelformset_factory(obj,max_num=1,widgets={'create_by':Select(attrs={'readonly':True})})

        if request.POST.get('ispost'):#submitting the form

            formset=formsetobject(request.POST)

            if formset.is_valid():
                

                #check if you are the creater of this entry, otherwise no permission!
                
                forms = formset.save(commit=False)

                banlist=[]
                for i in formset.changed_objects:
                    if 'create_by' in i[1]:
                        banlist.append(i[0])

                for i in forms:
                    if i.create_by==request.user and i not in banlist:
                        i.save()
                    else:
                        messages.error(request,"You can't either change user or change other user's setting")
                
                messages.success(request,'Entry Updated!')
        else:

            formset=formsetobject(queryset=obj.objects.filter(
                        pk__in=map(int,request.POST.getlist('selection'))
                        ),initial=[{'create_by':request.user}])

        return render(request,'project/filternedit.html',{'formset':formset,
                                                        'entry_list':entry_list,
                                                        'edit':edit,
                                                        'jsonstring':jsonstring})



