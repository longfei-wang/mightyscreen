#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from project import views

urlpatterns = patterns('',
    url(r'^projects', views.projects.as_view(), name='projects'),
    url(r'^projselect/', views.projselect.as_view(), name='projselect'),
    url(r'^projedit/', views.projedit.as_view(), name='projedit'),
    url(r'^jobview/', views.joblist.as_view(), name='jobview'),
    url(r'^job/(.+)', views.job.as_view(), name='job'),
    url(r'^filternedit/', views.filternedit.as_view(), name='filternedit'),
    )

