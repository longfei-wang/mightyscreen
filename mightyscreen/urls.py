from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'mightyscreen.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^main/', include('main.urls')),
    url(r'^account/', include('account.urls')),
    url(r'^process/', include('process.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

#=============================================================================
##tests from QY

urlpatterns += (
    url(r'^statistics/', include('statistics.urls')),
)
