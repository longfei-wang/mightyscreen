#utilities python module
from django.db.models import Count
from django.db import transaction
from main.models import submission,project
from django.core.urlresolvers import resolve
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

    def get(self,job_id):
        
        try:
            self.sub = submission.objects.get(id=job_id)
        except:
            pass

        return self



    def create(self,request=None,jobtype=None,log='',comments='',proj=None,user=None):
        
        if not jobtype:

            jobtype=resolve(request.path_info).url_name #default jobtype name is the view name (defined in url.py)

        """if everything is ready, create a pending job entry."""
        try:
            user=request.user
        except:
            pass

        if user.is_authenticated():#for demo use, no log will be recorded
            self.sub=submission(
            jobtype=jobtype,
            project=project.objects.get(pk=(request.session.get('proj_id') if request.session.get('proj_id') else 1)) if request else proj, #proj 1 is the demo project
            submit_by=request.user if request else user,
            submit_time=dt.datetime.now(),
            log=log,
            comments=comments,
            status='p')
            self.sub.save()

            return self.sub.id

        return None

    def update(self,progress='',log=''):
        """update logs and progress"""
        if self.sub:
            self.sub.log+=log#';plate: %s uploaded'%self.plates[pla]
            if progress:
                self.sub.progress=progress
            self.sub.save()

        return self

    def complete(self,log=''):
        if self.sub:
            self.sub.log+='Job completed at %s. '%dt.datetime.now().strftime("%x,%H:%M")+log
            self.sub.progress=100
            self.sub.status='c'
            self.sub.save()
        
        return self

    def fail(self,log=''):
        if self.sub:
            self.sub.log+=log
            self.sub.status='f'
            self.sub.save()
        
        return self

    def save_result(self,result):
        """Save result page/image for view later on. Note: result is a FileField objects"""
        if self.sub:
            self.sub.result=result

        return self

    def get_result(self,submission_id):
        if self.sub:
            sub=submission.objects.get(pk=submission_id)
            return sub.result
        return None

def get_related(plate):
    """a function that get all related project of a given project"""
    pass
