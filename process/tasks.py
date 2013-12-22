from __future__ import absolute_import
from celery.decorators import task
from process.models import stats
from django.db.models import Avg,StdDev
from django.core.urlresolvers import reverse
from async_messages import messages as umes
from django.contrib.auth.models import User
from celery.decorators import task

@task()
def process_score(data,proj,plates):
	"""A function that read user's equation and store the score into database
	currently very low speed, need code optimization"""
	agg=list()
	for i in proj.experiment.readout.all():
		agg.append("Avg('%(col)s'),StdDev('%(col)s')"%{'col':i.name})
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
		#pass stats to names spaces that user use
		for k in proj.experiment.readout.all():
			exec('%(readout)s_com_rep_avg=com["%(readout)s__avg"]'%{'readout':k.name})
			exec('%(readout)s_com_rep_sd=com["%(readout)s__stddev"]'%{'readout':k.name})
			exec('%(readout)s_pos_rep_avg=pos["%(readout)s__avg"]'%{'readout':k.name})
			exec('%(readout)s_pos_rep_sd=pos["%(readout)s__stddev"]'%{'readout':k.name})
			exec('%(readout)s_neg_rep_avg=neg["%(readout)s__avg"]'%{'readout':k.name})
			exec('%(readout)s_neg_rep_sd=neg["%(readout)s__stddev"]'%{'readout':k.name})

		for j in proj.rep():
			#individual plate
			#all wells
			exec('com=data.filter(plate=i,replicate=j,welltype="X").aggregate(%s)'%aggs)
			#positive wells
			exec('pos=data.filter(plate=i,replicate=j,welltype="P").aggregate(%s)'%aggs)
			#negative wells
			exec('neg=data.filter(plate=i,replicate=j,welltype="N").aggregate(%s)'%aggs)
			#pass stats to names spaces that user use
			for k in proj.experiment.readout.all():
				exec('%(readout)s_com_avg=com["%(readout)s__avg"]'%{'readout':k.name})
				exec('%(readout)s_com_sd=com["%(readout)s__stddev"]'%{'readout':k.name})
				exec('%(readout)s_pos_avg=pos["%(readout)s__avg"]'%{'readout':k.name})
				exec('%(readout)s_pos_sd=pos["%(readout)s__stddev"]'%{'readout':k.name})
				exec('%(readout)s_neg_avg=neg["%(readout)s__avg"]'%{'readout':k.name})
				exec('%(readout)s_neg_sd=neg["%(readout)s__stddev"]'%{'readout':k.name})
			#1-3*(FP_pos_sd+FP_neg_sd)/abs(FP_pos_avg-FP_neg_avg) Zscore for plate

			#calculate avg and sd of one well within all reps
			oneplate = data.filter(plate=i,welltype__in=['X','P','N'])
			for l in proj.plate.well():
				#one well of all replicates
				onewell=oneplate.filter(well=l)
				#raise Exception(dir(l))
				exec('rep=onewell.aggregate(%s)'%aggs)
				
				for k in proj.experiment.readout.all():
					exec('%(readout)s_rep_avg=rep["%(readout)s__avg"]'%{'readout':k.name})
					exec('%(readout)s_rep_sd=rep["%(readout)s__stddev"]'%{'readout':k.name})
				
				#calculate score based on user's equation for each well.	
				onerep=onewell.filter(replicate=j)
				x=onerep.first()
				#one well on a replicate plate				
				for k in proj.experiment.readout.all():
					exec('%(readout)s=float(x.%(readout)s)'%{'readout':k.name})
				
				for h in proj.score.all():
					try:
						score=eval(h.formular)
					except SyntaxError:
						return False
					exec ('onerep.update(%(name)s=%(value)s)'%{'name':h.name,'value':score})

	umes.success(proj.leader,'Score Updated. <a href="%s" class="alert-link">Go Check Out</a>'%reverse('view'))
	return True


