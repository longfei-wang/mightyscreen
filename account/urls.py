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
    url(r'^profile/', views.profile, name='profile'),
    url(r'^projects', views.projects, name='projects'),
    url(r'^projselect/', views.projselect, name='projselect'),
    url(r'^projedit/', views.projedit, name='projedit'),

    )



