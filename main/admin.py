from django.contrib import admin
from main.models import project, readout, readout_template, plate, score, score_template, submission

# Register your models here.

admin.site.register(project)
admin.site.register(readout)
admin.site.register(readout_template)
admin.site.register(plate)
admin.site.register(score)
admin.site.register(score_template)
admin.site.register(submission)
