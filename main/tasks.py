#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery.decorators import task


#wrap  rawdata class in a function for easier queue.
@task()
def queue(d,m):
    exec('d.%s'%m)
    return True


