from django.contrib import admin
from main.models import project, experiment, readout, fileformat, plate, score, submission

# Register your models here.

admin.site.register(project)
admin.site.register(experiment)
admin.site.register(readout)
admin.site.register(fileformat)
admin.site.register(plate)
admin.site.register(score)
admin.site.register(submission)
