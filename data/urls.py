#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from data import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'file', views.FileViewSet)


urlpatterns = patterns('',
    )

urlpatterns += router.urls