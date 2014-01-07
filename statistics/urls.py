#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from statistics import views

urlpatterns = patterns('',
    url(r'^$', views.heatmap.as_view(),name='stat_index'), #name='index' is conflict with main.index
    url(r'^details/', views.details.as_view(), name='c_details'),
    url(r'^heatmap/', views.heatmap.as_view(), name='stat_heatmap'),
    url(r'^correlation/', views.correlation.as_view(), name='stat_correlation'),
    url(r'^scatter/', views.scatter.as_view(), name='stat_scatter'),
    url(r'^histogram/', views.histogram.as_view(), name='stat_histogram'),
    url(r'^dendro/', views.dendrogram.as_view(), name='stat_dendrogram'),
    url(r'^dendro2d/', views.dendrogram2d.as_view(), name='stat_2ddendrogram'),
    )    

#==============================================================
##testing

urlpatterns +=(
    url(r'^test/', views.fingerprint_cluster, name='stat_test'),
)

