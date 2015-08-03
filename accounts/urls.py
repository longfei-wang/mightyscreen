#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static

from accounts import views
from django.contrib.auth.views import password_change,password_change_done,login,logout


urlpatterns = patterns('',
    url(r'^login/', login, {'template_name':'accounts/login.html'},name='login'),
    url(r'^password_change/', password_change, {'template_name':'accounts/password_change.html'},name='password_change'),
    url(r'^password_change_done/', password_change, {'template_name':'redirect.html',
    												'extra_context':{'message':'Password change successful','dest':'index'} 
    												},name='password_change_done'),
    url(r'^logout/', logout, {'template_name':'redirect.html',
    												'extra_context':{'message':'Logout successful','dest':'index'} 
    												},name='logout'),
    url(r'^register/', views.register, name='register'),
    url(r'^profile/', views.profile, name='profile'),
    )

