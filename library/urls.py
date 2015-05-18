#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from library import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'cmpd', views.CompoundViewSet)


urlpatterns = patterns('',
	# url(r'^cmpd/(?P<plate_well>[A-Z0-9]+)/$', views.json_compound_query),
	# url(r'^plate/(?P<plate>[A-Z0-9]+)/$', views.json_plate_query),
    )

urlpatterns += router.urls