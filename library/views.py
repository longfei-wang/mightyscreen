from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, detail_route
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from library.models import *
# Create your views here.



class CompoundViewSet(mixins.RetrieveModelMixin,viewsets.GenericViewSet):
	"""
 	given platewell and library name return the small molecule data in json
 	rest_framework
	"""
	queryset = compound.objects.all()
	serializer_class = compound_serializer
	lookup_field='plate_well'


	@detail_route(methods=['GET'])
	def plate(self,request,plate_well=None): #given plate and return the small molecule list in json
		plate = compound.objects.filter(plate=plate_well).values('plate_well','library_name__library_name')

		if len(plate) == 0:
			
			return HttpResponse(status =404)

		return Response(plate)

	# @detail_route(methods=['GET'])
	# def parse(self,request,pk=None): #The function to parse list csv file to database
	# 	return JSONResponse("parse called")
	
	# def perform_create(self,serializer): #called when upload a file
		
	# 	if not self.request.session.exists(self.request.session.session_key):
		
	# 		self.request.session.create() 
		
	# 	serializer.save(create_by=None if self.request.user.is_anonymous() else self.request.user,
	# 					session_id=self.request.session.session_key,
	# 					project_id=self.request.session.get('project_id',''))





# @api_view(['GET'])
# def json_compound_query(request,plate_well):
# 	"""
# 	given platewell and library name return the small molecule data in json
# 	rest_framework
# 	"""
# 	try:
# 		cmpd = compound.objects.get(plate_well=plate_well)
# 	except compound.DoesNotExist:
# 		return HttpResponse(status =404)

# 	if request.method == 'GET':
# 		serializer = compound_serializer(cmpd)
# 		return JSONResponse(serializer.data)


# @api_view(['GET'])
# def json_plate_query(request,plate):
# 	"""
# 	given plate and return the small molecule list in json
# 	rest_framework
# 	"""
# 	plate = compound.objects.filter(plate=plate).values('plate_well','library_name__library_name')
# 	if len(plate) == 0:
# 		return HttpResponse(status =404)

# 	if request.method == 'GET':
# 		#serializer = compound_serializer(plate, many=True)
# 		return JSONResponse(plate)