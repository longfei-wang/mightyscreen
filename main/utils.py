#utilities python module
from django.db.models import Count
from django.db import transaction
from main.models import submission
import datetime as dt

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




class job():

    """the job class, need test"""
    
    sub=None

    def create(self,request,jobtype,log='',comments=''):
        
        """if everything is ready, create a pending job entry."""
        self.sub=submission(
        jobtype=jobtype,
        project=project.objects.get(pk=(request.session.get('proj_id') if request.session.get('proj_id') else 1)), #proj 1 is the demo project
        submit_by=request.session.user,
        submit_time=dt.datetime.now(),
        status='p')
        self.sub.save()
        
        self.sub.log=log
        self.sub.comments=comments

        return self.sub.pk

    def update(self,progress,log=''):
        """update logs and progress"""
        self.sub.log+=log#';plate: %s uploaded'%self.plates[pla]
        self.sub.progress=progress
        self.sub.save()


    def complete(self):
        self.sub.log+='Job completed at %s'%dt.datetime.now()
        self.sub.status='c'
        self.sub.save()

    def fail(self):
        self.sub.status='f'
        self.sub.save()

    def save_result(self,result):
        self.sub.result=result

    def get_result(self,submission_id):
        sub=submission.objects.get(pk=submission_id)
        return sub.result
