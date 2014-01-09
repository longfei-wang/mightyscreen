from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from main.views import index

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index.as_view(), name='home'),
    url(r'^main/',include('main.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^process/', include('process.urls')),
    url(r'^statistics/', include('statistics.urls')),
    url(r'^admin/', include(admin.site.urls)),
   	url(r'^api/v2/', include('fiber.rest_api.urls')),
    url(r'^admin/fiber/', include('fiber.admin_urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',),}),
    url(r'^documents/', 'fiber.views.page',name='documents'),


    url(r'^media/(?P<path>.*)$','django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':False}),
)
