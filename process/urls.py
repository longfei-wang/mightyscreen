#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from process import views

urlpatterns = patterns('',
    url(r'^$', views.mark,name='process'),
    url(r'^mark', views.mark,name='mark'),
    url(r'^score', views.score,name='score'),
    )    



