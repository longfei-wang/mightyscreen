#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from account import views

urlpatterns = patterns('',
    url(r'^login/', views.signin, name='login'),
    url(r'^logout/', views.logoff, name='logout'),
    url(r'^register/', views.signup, name='register'),
    url(r'^my/', views.myaccount, name='myaccount'),
    url(r'^projselect/', views.projselect, name='projselect'),
    )    



