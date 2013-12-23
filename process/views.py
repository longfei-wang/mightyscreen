from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import messages
from main.models import project, data_base
from collections import OrderedDict as od
from process.tasks import process_score

# Create your views here.
    
def mark(request):
	if not 'proj' in request.session:
		return render(request,"main/error.html",{'error_msg':"No project specified!"})
	
	welltypes=od(sorted(dict(data_base.schoice).items()))
	proj=project.objects.get(pk=request.session['proj_id'])

	plates=['1','2']#updated model but table is hard to update, keep it this way for tmp

	# for i in proj.submission_plate_list_set.filter(status="s"):
	# 	plates.append(i.plate)

	if request.method=='POST':
		exec ('from data.models import proj_'+request.session['proj_id']+' as data')
    	if request.POST.getlist('plates'):

	    	for j in welltypes.keys():
	    		
	    		if request.POST.get(j):
	    			x=request.POST.get(j)
    				data.objects.filter(plate__in=request.POST.getlist('plates'),well__in=x.split(',')).update(welltype=j)


		messages.success(request,'WellType Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
	return render(request,'process/markwell.html',{'proj':proj,'welltypes':welltypes,'plates':plates})

def score(request):
	
	if not 'proj' in request.session:
		return render(request,"main/error.html",{'error_msg':"No project specified!"})
	
	proj=project.objects.get(pk=request.session['proj_id'])

	plates=['1','2']#updated model but table is hard to update, keep it this way for tmp

	# for i in proj.submission_plate_list_set.filter(status="s"):
	# 	plates.append(i.plate)


	if request.method=='POST':
		exec ('from data.models import proj_'+request.session['proj_id']+' as data')
		if request.POST.getlist('plates'):
			if process_score(data.objects.all(),proj,request.POST.getlist('plates')):
				messages.success(request,'Job has been sent. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
	return render(request,'process/score.html',{'plates':plates})