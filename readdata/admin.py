from django.contrib import admin
from readdata.models import readout_type, well, data

# Register your models here.

admin.site.register(readout_type)
admin.site.register(well)
admin.site.register(data)
