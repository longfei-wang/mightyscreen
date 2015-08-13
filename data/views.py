from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.response import Response
from django.core.files.base import ContentFile
from django.http import HttpResponse
from data.models import *
from data.csv_util import *
import os
from sets import Set
from django.db.models import Count
from collections import OrderedDict as odict
import json
import csv
# Create your views here.


# class MetaObject:
# 	"""
# 	Object that handle meta data
# 	"""
# 	meta = {}
# 	fields = []
# 	def __init__(self,_meta):
# 		self.meta = _meta
# 		if 'fields' in self.meta.keys():
# 			self.fields = self.meta['fields']

# 	@property
# 	def channels(self):
# 		"""
# 		a list of channels that has been used
# 		"""
# 		return [i['name'] for i in self.fields]

# 	@property
# 	def vchannels(self):
# 		"""
# 		a list of channels that has been used
# 		"""
# 		return [i['verbose'] for i in self.fields]

# 	@property
# 	def verbose(self):
# 		"""
# 		a dictionary with field name as key and verbose name as values
# 		"""
# 		v = {}
# 		for i in self.fields:
# 			v[i['name']] = i['verbose']

# 		return v


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

		self.project = find_or_create_project(self.request)
		#get_object_or_404(project,id=self.request.session.get('project',None))

		self.curPlate = get_curPlate(self.request)

		self.pdata = data.objects.filter(project=self.project)

		self.plate_list = [ i['plate'] for i in self.pdata.order_by('plate').values('plate').distinct()]
		
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
		print self.pdata
		keys = serializer.data[0].keys()

		with response as output_file:
			dict_writer = csv.DictWriter(output_file, keys)
			dict_writer.writeheader()
			dict_writer.writerows(serializer.data.results)

		return response



	@detail_route(methods=['GET'])
	def mark(self,request,plate_well):
		"""
		mark/unmark a compound as hit
		"""
		instance = get_object_or_404(self.get_queryset(),plate_well=plate_well)
		instance.hit = 1 if instance.hit == 0 else 0
		instance.save()

		hits_data = self.hits()

		return Response({
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			'mark':instance.hit,
			#'results':hits_data,
			})

	@detail_route(methods=['GET'])
	def setP(self,request,plate_well):
		"""
		mark/unmark a compound as positive control
		"""
		instance = get_object_or_404(self.get_queryset(),plate_well=plate_well)
		instance.welltype = 'P'
		instance.save()

		return Response({
			'success':True,
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			})

	@detail_route(methods=['GET'])
	def setN(self,request,plate_well):
		"""
		mark/unmark a compound as positive control
		"""
		instance = get_object_or_404(self.get_queryset(),plate_well=plate_well)
		instance.welltype = 'N'
		instance.save()

		return Response({
			'success':True,
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			})

	@detail_route(methods=['GET'])
	def setX(self,request,plate_well):
		"""
		mark/unmark a compound as positive control
		"""
		instance = get_object_or_404(self.get_queryset(),plate_well=plate_well)
		instance.welltype = 'X'
		instance.save()

		return Response({
			'success':True,
			'plate_well':plate_well,
			'curPlate':self.curPlate,
			})


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
		file_instance = get_object_or_404(csv_file,pk=pk)

		project =find_or_create_project(request)

		inputfile = file_instance.raw_csv_file
		
		results = checklist(inputfile.path)

		return Response(results)

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


		file_instance = get_object_or_404(csv_file,pk=pk)

		project =find_or_create_project(request)

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

		return Response("parsed")
	
	def perform_create(self,serializer): #called when upload a file
		
		serializer.save(project=find_or_create_project(self.request))

