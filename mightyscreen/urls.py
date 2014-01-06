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
    url(r'^media/(?P<path>.*)$','django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':False}),
)
