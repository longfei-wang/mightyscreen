from django.contrib import admin

from library.models import compound, additional_compound_info, library, sub_library



admin.site.register(compound)
admin.site.register(additional_compound_info)
admin.site.register(library)
admin.site.register(sub_library)