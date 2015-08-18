from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib.auth.models import User
from data.models import *
from data.csv_util import *
import os
from sets import Set
from django.db.models import Count
from collections import OrderedDict as odict
import json
import csv
# Create your views here.

class ProjectViewSet(mixins.RetrieveModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
	
	queryset = project.objects.all()
	serializer_class = ProjectSerializer

	def get_queryset(self):

		return [] if self.request.user.is_anonymous() else project.objects.filter(user=self.request.user) #anonymous dont have any right other than create new project.
	
	def perform_create(self, serializer):
		serializer.save(user=self.request.user)

	def list(self):
		return Response({
			'results':'not allowed'
			},status=status.HTTP_405_METHOD_NOT_ALLOWED)

	def retrieve(self):
		return Response({
			'results':'not allowed'
			},status=status.HTTP_405_METHOD_NOT_ALLOWED)

	@detail_route(methods=['GET'])
	def use(self,request,pk):
		"""
		to change current project
		"""
		request.session['project'] = self.get_object().id.hex
		request.session['project_name'] = self.get_object().name

		return redirect('tableview')

	@detail_route(methods=['GET'])
	def rename(self,request,pk):
		"""
		rename current project
		"""
		p = self.get_object()
		new_name = request.GET.get('name',None)


		if new_name:
			p.name = new_name
			p.save()
			request.session['project_name'] = p.name

			return Response({'results':'success','name':p.name},status=status.HTTP_200_OK)

		return Response({'results':'fail: no name provided'},status=status.HTTP_404_NOT_FOUND)
	
	@detail_route(methods=['GET'])
	def delete(self,request,pk):
		"""
		delete current project
		"""
		p = self.get_object()
		if p.id.hex == request.session.get('project',None):
			request.session['project'] = None
			request.session['project_name'] = ''
			get_or_create_project(request)

		p.delete()

		return Response({'results':'success'},status=status.HTTP_200_OK)

	@list_route()
	def new(self,request):
		"""
		create a new project
		"""
		p = create_project(request)
		request.session['project'] = p.id.hex
		request.session['project_name'] = p.name		
		return redirect('tableview')


class DataViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
	"""
	populate data based on query
	"""
	queryset = data.objects.all()
	serializer_class = DataSerializer
	lookup_field='plate_well'
	project=None
	pdata=None
	plate_list=[]
	curPlate = None
	channels = []

	def get_queryset(self):

		self.project = get_or_create_project(self.request)
		#get_object_or_404(project,id=self.request.session.get('project',None))

		self.pdata = self.project.data_set

		self.plate_list = self.project.get_plate_list()

		self.curPlate = self.project.get_curPlate(self.request)

		curPlateData = self.pdata.filter(plate=self.curPlate)

		self.channels = curPlateData[0].readouts.keys() if len(curPlateData) > 0 else []

		return curPlateData

	def list(self,request):
		"""
		list view
		"""

		response = super(DataViewSet,self).list(request)
		
		response.data.update({
			'plateList':self.plate_list,
			'curPlate':self.curPlate,
			'channels':self.channels,
			})

		return response

	@list_route()
	def to_csv(self,request):
		"""
		conver all project data to csv for user to download.
		"""

		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment;filename="export.csv"'

		self.get_queryset()
		serializer = self.serializer_class(self.pdata,many=True)
		
		unique_keys = set()
		for i in serializer.data:
			unique_keys.update(i.keys())
		
		keys = serializer.data[0].keys()
		for i in unique_keys:
			if i not in keys:
				keys.append(i)

		dict_writer = csv.DictWriter(response, keys, restval='', extrasaction='ignore',quotechar='"',quoting=True)
		dict_writer.writeheader()
		dict_writer.writerows(serializer.data)

		return response


	@list_route()
	def demo(self,request):
		"""
		to load demo into current project.
		demo will be copies from User: demo.
		"""
		
		try:
			demo = User.objects.get(username='demo')
			demo_data = demo.project_set.first().data_set.all()
		except:
			return redirect('uploadview')

		self.get_queryset()
		self.pdata.all().delete()#all previous data will be deleted
		

		def query2object(d,project,chunk_size=100):
			"""
			convert a data query to a new data objects that can be parsed into database
			in the mean time create meta data for this data
			"""
			l = []
			for i in d:
				
				dataDict = {
					'project': self.project,
					'plate_well': i.plate_well,
					'plate': i.plate,
					'well': i.well,
					'welltype': i.welltype,
					'hit': i.hit,
					'identifier': i.identifier,
					'readouts':i.readouts,
				}
				
				l.append(data(**dataDict))

				if len(l)>=chunk_size:
					yield l
					l = []

			yield l

		for i in query2object(demo_data,self.project):
			data.objects.bulk_create(i)

		return redirect('tableview')

	@detail_route(methods=['GET'])
	def mark(self,request,plate_well):
		"""
		mark/unmark a compound as hit
		"""
		instance = self.get_object()
		instance.hit = 1 if instance.hit == 0 else 0
		instance.save()

		#hits_data = self.hits()

		return Response({
			'results':'success',
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			'mark':instance.hit,
			#'results':hits_data,
			},status=status.HTTP_200_OK)

	@detail_route(methods=['GET'])
	def setP(self,request,plate_well):
		"""
		mark/unmark a compound as positive control
		"""
		instance = self.get_object()
		instance.welltype = 'P'
		instance.save()

		return Response({
			'results':'success',
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			},status=status.HTTP_200_OK)

	@detail_route(methods=['GET'])
	def setN(self,request,plate_well):
		"""
		mark/unmark a compound as positive control
		"""
		instance = self.get_object()
		instance.welltype = 'N'
		instance.save()

		return Response({
			'results':'success',
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			},status=status.HTTP_200_OK)

	@detail_route(methods=['GET'])
	def setX(self,request,plate_well):
		"""
		mark/unmark a compound as positive control
		"""
		instance = self.get_object()
		instance.welltype = 'X'
		instance.save()

		return Response({
			'results':'success',
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			},status=status.HTTP_200_OK)


	def hits(self):
		"""
		return a list of hits on current plate 
		"""

		hits_query = self.get_queryset().filter(hit=1)
		serializer = self.serializer_class(hits_query,many=True)

		return serializer.data #hit_list and data returned will not be the same. Some marked hit compound doesn't exists in library.


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
		file_instance = self.get_object()

		project =get_or_create_project(request)

		inputfile = file_instance.raw_csv_file
		
		results = checklist(inputfile.path)

		return Response(results,status=status.HTTP_200_OK)

	@detail_route(methods=['POST'])
	def parse(self,request,pk=None): #The function to parse list csv file to database
		"""
		take the list file and convert it to a format that can be used by front end.
		"""

		def dict2object(d,project,chunk_size=100):
			"""
			convert a dict that has platewell as key, to data objects that can be parsed into database
			in the mean time create meta data for this data
			"""
			l = []
			for k,v in d.iteritems():
				
				dataDict = {
					'project': project,
					'plate_well': k,
					'plate': v['plate'],
					'well': v['well'],
					'welltype': v['welltype'],
					'identifier': v['identifier'],
					'readouts':odict(),
				}
				

				for kk,vv in v['readouts'].iteritems():
					
					for i,item in enumerate(vv):
						dataDict['readouts'][kk+("" if i == 0 else "_"+str(i))] = float(item)


				l.append(data(**dataDict))

				if len(l)>=chunk_size:
					yield l
					l = []


			yield l


		file_instance = self.get_object()

		project =get_or_create_project(request)

		d = request.POST

		readouts = d.getlist('readouts[]')

		identifier = d.get('identifier',None)

		plates = odict() #plates is a dictionary converting old plate number to new plate number.
		for i,item in enumerate(d.getlist('oplates[]')):
			plates[item] = d.getlist('plates[]')[i]

		print plates.values()

		f = file_instance.raw_csv_file

		#check if plate already exists in database if so delete
		data.objects.filter(project=project,plate__in=set(plates.values())).delete()

		for i in dict2object(file2dict(f.path,plates,readouts,identifier),project):
			data.objects.bulk_create(i)
		# meta['positives'] = d.getlist('positives[]')
		# meta['negatives'] = d.getlist('negatives[]')

		#bulk create data. This is much faster than 1 by 1
		# chunk_size = 100
		# for i in range(0,len(dataList),chunk_size):
		# 	data.objects.bulk_create(dataList[i:i+chunk_size])

		#set controls

		# all_parsed_data = data.objects.filter(plate__in=set(plates.values()))
		# all_parsed_data.filter(well__in=meta['positives']).update(welltype='P')
		# all_parsed_data.filter(well__in=meta['negatives']).update(welltype='N')

		#update the meta data of this project
		# project.meta = meta
		# project.save()

		return Response({"results":"parsed"},status=status.HTTP_201_CREATED)
	
	def perform_create(self,serializer): #called when upload a file
		
		serializer.save(project=get_or_create_project(self.request))

