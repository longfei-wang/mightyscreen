#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


from statistics import views


urlpatterns = patterns('',
    url(r'^$', views.index,name='statindex'), #name='index' is conflict with main.index
    url(r'^plot/', views.plot, name='plot'),
    )    



