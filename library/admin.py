from django.contrib import admin

from library.models import compound, library, sub_library



admin.site.register(compound)
admin.site.register(library)
admin.site.register(sub_library)