from django.contrib import admin
from main.models import project, data, experiment, readout, fileformat, plate
from main.models import compound, library_info,chemical_info

# Register your models here.

admin.site.register(project)
admin.site.register(data)
admin.site.register(experiment)
admin.site.register(readout)
admin.site.register(fileformat)
admin.site.register(plate)
admin.site.register(compound)
admin.site.register(library_info)
admin.site.register(chemical_info)