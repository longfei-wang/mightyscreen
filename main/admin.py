from django.contrib import admin
from main.models import project, experiment, readout, fileformat, plate

# Register your models here.

admin.site.register(project)
admin.site.register(experiment)
admin.site.register(readout)
admin.site.register(fileformat)
admin.site.register(plate)
