#utilities python module
from django.db.models import Count
from django.db import transaction

def get_platelist(proj_id,withtime=True):#get the platelists of current project, ranked by time
	exec ('from data.models import proj_'+proj_id+' as data')
	plates=list()
	for i in list(data.objects.order_by('-create_date','plate').values('plate','create_date').annotate(x=Count('plate'))):
		plates.append(i['plate'])
	# plates=sorted(plates)
	raise Exception(plates)



@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    """
    transaction.commit()

