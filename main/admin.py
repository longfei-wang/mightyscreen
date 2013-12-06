from django.contrib import admin
from main.models import project, data, experiment, readout, fileformat, plate
from main.models import compound, additional_compound_info, library, sub_library

# Register your models here.

admin.site.register(project)
admin.site.register(data)
admin.site.register(experiment)
admin.site.register(readout)
admin.site.register(fileformat)
admin.site.register(plate)
admin.site.register(compound)
admin.site.register(additional_compound_info)
admin.site.register(library)
admin.site.register(sub_library)