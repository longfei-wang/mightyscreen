#utilities python module
from django.db.models import Count
from django.db import transaction

def get_platelist(**kwargs):
	
    """get the platelists of current project, 
    can use model, or a project_id, order by create_date)
    proj_id=xxx or model=xxx"""
    
    if 'proj_id' in kwargs:
        exec ('from data.models import proj_'+kwargs['proj_id']+' as data')
    elif 'model' in kwargs:
        data=kwargs['model']
    else:
        return []

    plates=list()
    for i in list(data.objects.order_by('-create_date','plate').values('plate','create_date').annotate(x=Count('plate'))):
    	plates.append(i['plate'])

    return plates


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

