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
		
		file_instance = get_object_or_404(csv_file,pk=pk)
		file_instance.cleaned_csv_file.save(os.path.join('CSV',pk+'.csv'),file_instance.raw_csv_file)

		inputfile = file_instance.raw_csv_file
		outputfile = file_instance.cleaned_csv_file

		results = grid2list(inputfile,outputfile)

		inputfile.close()
		outputfile.close()

		if 'is_list' in results.keys():

			listfile = file_instance.cleaned_csv_file
			
			results = checklist(listfile)
			
			listfile.close()

		return Response(results)

	@detail_route(methods=['GET'])
	def parse(self,request,pk=None): #The function to parse list csv file to database
		return Response("parse called")
	
	def perform_create(self,serializer): #called when upload a file
		
		if not self.request.session.exists(self.request.session.session_key):
		
			self.request.session.create() 
		
		serializer.save(create_by=None if self.request.user.is_anonymous() else self.request.user,
						session_id=self.request.session.session_key,
						project_id=self.request.session.get('project_id',''))



