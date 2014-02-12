from __future__ import absolute_import
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from celery.decorators import task
from django.contrib import messages
from process.utils import ScoreReader
from main.models import *
import process.readers as readers

@task()
def process_score(data,proj,plates,datamodel):
	"""A function that read user's equation and store the score into database
	currently very low speed, need code optimization. A celery wrapper for readerscore class"""
	x=ScoreReader(proj,datamodel)

	for i in plates:
		x.flush()#flush the cache

		#calculate avg and sd of one well within all reps
		for l in data.filter(plate=i):
			
			#calculate score based on user's equation for each well.	
			for h in proj.score.all():

				score=x.parse(l,h.formular)

				
				exec ('l.score["%(name)s"]=%(value)s'%{'name':h.name,'value':score})
			l.save()

	#umes.success(proj.leader,'Score Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
	return True



from jobtastic import JobtasticTask

class savethefile(JobtasticTask):
    """
    Division is hard. Make Celery do it a bunch.
    """
    # These are the Task kwargs that matter for caching purposes
    significant_kwargs = [
        ('param', str),
    ]
    # How long should we give a task before assuming it has failed?
    herd_avoidance_timeout = 60  # Shouldn't take more than 60 seconds
    # How long we want to cache results with identical ``significant_kwargs``
    cache_duration = 0  # Cache these results forever. Math is pretty stable.
    # Note: 0 means different things in different cache backends. RTFM for yours.

    def calculate_result(self, param,**kwargs):
        """
        MATH!!!
        """
        # Only actually update the progress in the backend every 10 operations

        results=readers.reader(param=param).parse().save(self)
            
        # Let's let everyone know how we're doing
        
        return results



