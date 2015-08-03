from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$',TemplateView.as_view(template_name="index.html"),name='index'),
    url(r'^upload/',TemplateView.as_view(template_name="upload.html"),name='uploadview'),
    url(r'^table/',TemplateView.as_view(template_name="tableview.html"),name='tableview'),
    url(r'^plate/',TemplateView.as_view(template_name="plateview.html"),name='plateview'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('library.urls')),
    url(r'^api/', include('data.urls')),
    url(r'^accounts/', include('accounts.urls')),
)
