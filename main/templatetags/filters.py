# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 22:40:26 2013

@author: longfei
"""
from django import template

register = template.Library()

@register.filter
def getattr (obj, args):
    """From djangosnippets: 
    {% if block|getattr:"editable," %}
    """
    splitargs = args.split(',')
    try:
      (attribute, default) = splitargs
    except ValueError:
      (attribute, default) = args, ''

    try:
      attr = obj.__getattribute__(attribute)
    except AttributeError:
      attr = obj.__dict__.get(attribute, default)
    except:
      attr = default

    if hasattr(attr, '__call__'):
        return attr.__call__()
    else:
        return attr