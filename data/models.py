from django.db import models
from main.models import data_base,project
# Create your models here.

#automatically generate data model(table) for each project with their specific readouts
#figured that the table would be too big to store all the data. 
#A HTS project can easily have millions of entries. Better handle project seperately
for i in project.objects.all():
    n=''
    for j in i.experiment.readout.all():

        n+=j.name+'=models.TextField();'

    exec ('class proj_'+str(i.pk)+'(data_base):'+n)





