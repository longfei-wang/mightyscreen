from __future__ import absolute_import
from django.core.urlresolvers import reverse
from async_messages import messages as umes
from django.contrib.auth.models import User
from celery.decorators import task
from django.contrib import messages
from process.utils import ScoreReader
@task()
def process_score(data,proj,plates):
	"""A function that read user's equation and store the score into database
	currently very low speed, need code optimization"""
	x=ScoreReader(proj)

	for i in plates:
		x.flush()#flush the cache

		#calculate avg and sd of one well within all reps
		for l in data.filter(plate=i,welltype__in=['X','P','N']):
			
			#calculate score based on user's equation for each well.	
			for h in proj.score.all():
				try:
					score=x.parse(l,h.formular)
				except SyntaxError:
					return False
				
				exec ('l.%(name)s=%(value)s'%{'name':h.name,'value':score})
			l.save()

	#umes.success(proj.leader,'Score Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
	return True


