#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from main import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^upload/', views.upload, name='upload'),
    


#==============================================================================
## test urls from QY    
    url(r'^tasks/', views.tasks, name='tasks'),
#    url(r'^submit/', views.submit_table, name='submit1'),
    url(r'^submit2/', views.submit_analysis, name='submit2'),
    url(r'^submit/', views.upload_raw_datafile.as_view(), 
        name = "submit1"),
    
#    url(r'^uploaded/(?P<pk>\d+)/$',views.tasks, name ="upload_success"),
#   url(r'^gen/', views.gen, name='gen'),
) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )

