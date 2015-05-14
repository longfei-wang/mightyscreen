from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from library.models import *
# Create your views here.

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view(['GET'])
def json_compound_query(request,plate_well):
	"""
	given platewell and library name return the small molecule data in json
	rest_framework
	"""
	try:
		cmpd = compound.objects.get(plate_well=plate_well)
	except compound.DoesNotExist:
		return HttpResponse(status =404)

	if request.method == 'GET':
		serializer = compound_serializer(cmpd)
		return JSONResponse(serializer.data)


@api_view(['GET'])
def json_plate_query(request,plate):
	"""
	given plate and return the small molecule list in json
	rest_framework
	"""
	plate = compound.objects.filter(plate=plate).values('plate_well','library_name__library_name')
	if len(plate) == 0:
		return HttpResponse(status =404)

	if request.method == 'GET':
		#serializer = compound_serializer(plate, many=True)
		return JSONResponse(plate)