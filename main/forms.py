#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms


class UploadFileForm(forms.Form):
    """to longfei: I change the name from file to datafile
    because file is a type name, could cause error"""
        
    #title = forms.CharField(max_length=50)
    
    library = forms.CharField()    
    plates = forms.CharField()
    datafile  = forms.FileField()
    comment = forms.CharField(widget=forms.Textarea,required=False)
    