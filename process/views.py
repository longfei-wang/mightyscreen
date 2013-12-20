from django.shortcuts import render
from django.core.context_processors import csrf
from main.models import project, data_base
# Create your views here.
    
def mark(request):
	
	welltypes=dict(data_base.schoice)
	proj=project.objects.get(pk=request.session['proj_id'])

	plates=['1','2']#updated model but table is hard to update, keep it this way for tmp

	# for i in proj.submission_plate_list_set.filter(status="s"):
	# 	plates.append(i.plate)


	if request.method=='POST':
		if not 'proj' in request.session:
			return render(request,"main/error.html",{'error_msg':"No project specified!"})
         
    	exec ('from data.models import proj_'+request.session['proj_id']+' as data')

    	if request.POST.getlist('plates'):
	    	for i in request.POST.getlist('plates'):
	    		for j in welltypes.keys():

	    			if request.POST.get(j):
	    				x=request.POST.get(j)
	    				for h in x.split(','):
	    					data.objects.filter(plate=i,well=h).update(welltype=j)


		# raise Exception(request.POST.getlist('plates'))
	return render(request,'process/markwell.html',{'proj':proj,'welltypes':welltypes,'plates':plates})
