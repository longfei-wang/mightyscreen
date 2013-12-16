#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


from statistics import views


urlpatterns = patterns('',
    url(r'^$', views.index,name='statindex'), #name='index' is conflict with main.index
    url(r'^compounds/', views.compound_list, name='compounds'),
    url(r'^details/', views.details, name='c_details'),
    url(r'^plot/', views.heatmap, name='c_details'),
    )    



