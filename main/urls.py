#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from main import views

urlpatterns = patterns('',
    url(r'^$', views.index,name='index'),
    url(r'^view/', views.datalist, name='view'),
    url(r'^upload/', views.upload, name='upload'),
    url(r'^export/', views.export, name='export'),

    )    



