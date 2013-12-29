#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from statistics import views


urlpatterns = patterns('',
    url(r'^$', views.index,name='stat_index'), #name='index' is conflict with main.index
    url(r'^details/', views.details, name='c_details'),
    url(r'^heatmap/', views.heatmap, name='stat_heatmap'),
    url(r'^replicates/', views.replicates, name='stat_replicates'),
    url(r'^scatter/', views.scatter, name='stat_scatter'),
    )    



