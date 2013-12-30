#utilities python module
from django.db.models import Count

def get_platelist(proj_id,withtime=True):#get the platelists of current project, ranked by time
	exec ('from data.models import proj_'+proj_id+' as data')
	plates=list()
	for i in list(data.objects.order_by('-create_date','plate').values('plate','create_date').annotate(x=Count('plate'))):
		plates.append(i['plate'])
	# plates=sorted(plates)
	raise Exception(plates)