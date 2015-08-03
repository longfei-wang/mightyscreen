# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 22:40:26 2013

@author: longfei
"""
from django import template
from django.db import models
from datetime import datetime
import re

register = template.Library()

@register.filter
def getattr (obj, args):
    """From djangosnippets: 
    {% if block|getattr:"editable," %}
    """
    if not obj:
      return ''

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

@register.filter
def tabler(value):
  """filter that format data of tables, make them compact
  useage: {value|tabler}"""
  if isinstance(value,datetime):
    return value.strftime("%x,%H:%M")

  if isinstance(value,float):
    if value > 10000:
      return "{:5.2E}".format(value)
    else:
      return "{:5.2f}".format(value) 
  return value


@register.filter
def paragraphs(value):
  """
  Turns paragraphs delineated with newline characters into
  paragraphs wrapped in <p> and </p> HTML tags.
  """
  paras = re.split(r'[\r\n]+', value)
  paras = ['<p>%s</p>' % p.strip() for p in paras]
  return '\n'.join(paras)
  paragraphs = stringfilter(paragraphs)


@register.filter
def lookup(value,arg):
  """filter for dictionary and list"""
  if isinstance(value,dict):
    return value[arg]
  elif isinstance(value,list):
    return value[arg]