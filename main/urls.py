#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from main import views

urlpatterns = patterns('',
    url(r'^$', views.index.as_view(),name='index'),
    url(r'^getview/([0-9a-fxA-FX]+)', views.get_view.as_view(),name='get_view'),
    url(r'^view/', views.datalist.as_view(), name='view'),
    url(r'^saveview/', views.save_view.as_view(), name='save_view'),
    url(r'^export/', views.export.as_view(), name='export'),
    url(r'^addtohitlist/', views.addtohitlist.as_view(), name='addtohitlist'),
    )    

