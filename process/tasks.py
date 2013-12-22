from __future__ import absolute_import
from celery.decorators import task
from process.models import stats
from django.db.models import Avg,StdDev

def process_score(data,proj,plates):
	"""A function that read user's equation and store the score into database"""
	agg=list()
	for i in proj.experiment.readout.all():
		agg.append("Avg('%(col)s'),StdDev('%(col)s')"%{'col':i.name})
	aggs=",".join(agg)
	
	for i in plates:
		for j in proj.rep():
			#all wells
			exec('all=data.filter(plate=i,replicate=j,welltype__in=["X","P","N"]).aggregate(%s)'%aggs)
			#positive wells
			exec('pos=data.filter(plate=i,replicate=j,welltype="P").aggregate(%s)'%aggs)
			#negative wells
			exec('neg=data.filter(plate=i,replicate=j,welltype="N").aggregate(%s)'%aggs)
			#pass stats to names spaces that user use
			for k in proj.experiment.readout.all():
				exec('%(readout)s_all_avg=all["%(readout)s__avg"]'%{'readout':k.name})
				exec('%(readout)s_all_sd=all["%(readout)s__stddev"]'%{'readout':k.name})
				exec('%(readout)s_pos_avg=pos["%(readout)s__avg"]'%{'readout':k.name})
				exec('%(readout)s_pos_sd=pos["%(readout)s__stddev"]'%{'readout':k.name})
				exec('%(readout)s_neg_avg=neg["%(readout)s__avg"]'%{'readout':k.name})
				exec('%(readout)s_neg_sd=neg["%(readout)s__stddev"]'%{'readout':k.name})
			#1-3*(FP_pos_sd+FP_neg_sd)/abs(FP_pos_avg-FP_neg_avg) Zscore for plate

			#calculate the score for each well
			for l in data.filter(plate=i,replicate=j,welltype='X'):
				for h in proj.score.all():
					score=eval(h.formular)
					raise Exception('l.update(%(name)s=%(value)s)'%{'name':h.name,'value':score})

	# exec('a=data.aggregate(%s)'%aggs)
	# raise Exception(a)
		# i.name_pos_avg=
		# i.name_pos_sd=

		# i.name_neg_avg=
		# i.name_neg_sd=
		
		# i.name_all_avg=
		# i.name_all_sd=