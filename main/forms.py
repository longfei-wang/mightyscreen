#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms


class UploadFileForm(forms.Form):
    """to longfei: I change the name from file to datafile
    because file is a type name, could cause error"""
        
    #title = forms.CharField(max_length=50)
    project = forms.CharField(widget=forms.HiddenInput)
    user = forms.CharField(widget=forms.HiddenInput)
    library = forms.CharField()
    plates = forms.CharField()
    datafile  = forms.FileField()
    comments = forms.CharField(widget=forms.Textarea,required=False)
    