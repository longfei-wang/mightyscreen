#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from main import views

urlpatterns = patterns('',
    url(r'^$', views.index.as_view(),name='index'),
    url(r'^getview/([0-9a-fxA-FX]+)', views.get_view.as_view(),name='get_view'),
    url(r'^view/', views.datalist.as_view(), name='view'),
    url(r'^saveview/', views.save_view.as_view(), name='save_view'),
    url(r'^export/', views.export.as_view(), name='export'),
    url(r'^addtohitlist/', views.addtohitlist.as_view(), name='addtohitlist'),
    url(r'^tablefeed/', TemplateView.as_view(template_name="main/datatable.html"), name='tablefeed'),
    url(r'^table/', views.table.as_view(), name='table'),
    )    

