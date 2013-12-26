from __future__ import absolute_import
from celery.decorators import task
from process.models import stats
from django.db.models import Avg,StdDev
from django.core.urlresolvers import reverse
from async_messages import messages as umes
from django.contrib.auth.models import User
from celery.decorators import task
from django.contrib import messages

@task()
def process_score(data,proj,plates):
	"""A function that read user's equation and store the score into database
	currently very low speed, need code optimization"""
	agg=list()
	for i in proj.experiment.readout.all():
		for j in proj.rep():
			agg.append("Avg('%(col)s_%(rep)s'),StdDev('%(col)s_%(rep)s')"%{'col':i.name,'rep':j})
	aggs=",".join(agg)
	#first calculate all the constants name space user can use, eg:
	# FP_pos_avg
	# FP_pos_sd
	for i in plates:
		#include all replicate plates
		#all wells
		exec('com=data.filter(plate=i,welltype="X").aggregate(%s)'%aggs)
		#positive wells
		exec('pos=data.filter(plate=i,welltype="P").aggregate(%s)'%aggs)
		#negative wells
		exec('neg=data.filter(plate=i,welltype="N").aggregate(%s)'%aggs)

		#it is likely that no positive or negative control is marked
		if not (pos and neg):
			messages.error(request,'No Positive/Negative control on plate %s'%i)

		for j in proj.rep():

			#pass stats to names spaces that user use
			for k in proj.experiment.readout.all():

				exec('%(readout)s_%(rep)s_com_avg=com["%(readout)s_%(rep)s__avg"]'%{'readout':k.name,'rep':j})
				exec('%(readout)s_%(rep)s_com_sd=com["%(readout)s_%(rep)s__stddev"]'%{'readout':k.name,'rep':j})
				exec('%(readout)s_%(rep)s_pos_avg=pos["%(readout)s_%(rep)s__avg"]'%{'readout':k.name,'rep':j})
				exec('%(readout)s_%(rep)s_pos_sd=pos["%(readout)s_%(rep)s__stddev"]'%{'readout':k.name,'rep':j})
				exec('%(readout)s_%(rep)s_neg_avg=neg["%(readout)s_%(rep)s__avg"]'%{'readout':k.name,'rep':j})
				exec('%(readout)s_%(rep)s_neg_sd=neg["%(readout)s_%(rep)s__stddev"]'%{'readout':k.name,'rep':j})
			#1-3*(FP_pos_sd+FP_neg_sd)/abs(FP_pos_avg-FP_neg_avg) Zscore for plate

		#calculate avg and sd of one well within all reps
		for l in data.filter(plate=i,welltype__in=['X','P','N']):
			#calculate score based on user's equation for each well.	
			for j in proj.rep():
				#one well				
				for k in proj.experiment.readout.all():
					exec('%(readout)s_%(rep)s=l.%(readout)s_%(rep)s'%{'readout':k.name,'rep':j})
				
			for h in proj.score.all():
				try:
					score=eval(h.formular)
				except SyntaxError:
					return False
				
				exec ('l.%(name)s=%(value)s'%{'name':h.name,'value':score})
			l.save()

	umes.success(proj.leader,'Score Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
	return True


