from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response
from django.core.files.base import ContentFile
from data.models import *


from data.grid2list import grid2list, checklist
import os
# Create your views here.


class FileViewSet(mixins.RetrieveModelMixin,mixins.CreateModelMixin,viewsets.GenericViewSet):
	"""
	upload a csvfile
	"""
	queryset = csv_file.objects.all()
	serializer_class = csv_file_serializer

	@detail_route(methods=['GET'])
	def clean(self,request,pk=None): #The function to convert raw csv file to list csv file
		"""
		inputfile is a grid file/list file
		outputfile is a list file
		"""
		file_instance = get_object_or_404(csv_file,pk=pk)

		inputfile = file_instance.raw_csv_file
		outputfile = ContentFile('')#file_instance.cleaned_csv_file

		inputfile.open(mode='rb')
		outputfile.open(mode='w')

		results = grid2list(inputfile,outputfile)
		
		if 'is_list' in results.keys():
			
			inputfile.open(mode='rb')

			results = checklist(inputfile)

			inputfile.open(mode='rb')

			outputfile = ContentFile(inputfile.read())

		file_instance.cleaned_csv_file.save(os.path.join('CSV',pk+'.csv'),outputfile)

		inputfile.close()
		outputfile.close()

		return Response(results)

	@detail_route(methods=['POST'])
	def parse(self,request,pk=None): #The function to parse list csv file to database
		"""
		take the list file and convert it to a format that can be used by front end.
		"""
		return Response("parse called")
	
	def perform_create(self,serializer): #called when upload a file
		
		serializer.save(project=find_or_create_project(self.request))

