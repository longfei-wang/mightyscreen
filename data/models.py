from django.db import models
from main.models import data_base,project
# Create your models here.

#automatically generate data model(table) for each project with their specific readouts
#figured that the table would be too big to store all the data. 
#A HTS project can easily have millions of entries. Better handle project seperately
if project.objects.all():
	for i in project.objects.all():
	    n=''
	    for j in i.experiment.readout.all():
	    	for h in i.rep():

	    	    n+='%(readout)s_%(rep)s=models.FloatField(null=True);'%{'readout':j,'rep':h}
	    
	    for l in i.score.all():
	        
	        n+=l.name+'=models.FloatField(null=True);'
	    
	    #raise Exception(n)
	    exec ('class proj_'+str(i.pk)+'(data_base):'+n)



