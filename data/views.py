from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.response import Response
from django.core.files.base import ContentFile
from data.models import *
import os
from sets import Set
from django.db.models import Count
from collections import OrderedDict as odict
# Create your views here.


class MetaObject:
	"""
	Object that handle meta data
	"""
	meta = {}
	fields = []
	def __init__(self,_meta):
		self.meta = _meta
		if 'fields' in self.meta.keys():
			self.fields = self.meta['fields']

	@property
	def channels(self):
		"""
		a list of channels that has been used
		"""
		return [i['name'] for i in self.fields]

	@property
	def vchannels(self):
		"""
		a list of channels that has been used
		"""
		return [i['verbose'] for i in self.fields]

	@property
	def verbose(self):
		"""
		a dictionary with field name as key and verbose name as values
		"""
		v = {}
		for i in self.fields:
			v[i['name']] = i['verbose']

		return v


class DataViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
	"""
	populate data based on query
	"""
	queryset = data.objects.all()
	serializer_class = DataSerializer
	lookup_field='plate'
	project=None
	plate_list=[]
	curPlate = None
	meta=None

	def get_queryset(self):

		self.project = find_or_create_project(self.request)
		#get_object_or_404(project,id=self.request.session.get('project',None))
		
		self.meta = MetaObject(self.project.meta)

		self.curPlate = get_curPlate(self.request)

		pdata = data.objects.filter(project=self.project)

		self.plate_list = [ i['plate'] for i in \
		pdata.order_by('plate').values('plate').distinct()]
		
		return pdata.filter(plate=self.curPlate)

	def list(self,request):
		"""
		list view
		"""

		response = super(DataViewSet,self).list(request)

		hit_list, hit_prop = self.hits(request)
		
		response.data.update({
			'plateList':self.plate_list,
			'curPlate':self.curPlate,
			'hitList':hit_list,
			'hitProp':hit_prop,
			'channels':self.meta.vchannels,
			'meta':self.project.meta,
			})

		return response

	@detail_route(methods=['GET'])
	def mark(self,request,plate_well):
		"""
		mark/unmark a compound as hit
		"""
		instance, created = hitlist.objects.get_or_create(project=self.project,plate_well=plate_well)
		if not created:
			instance.delete()

		hit_list, hit_prop = self.hits(request)
		return Response({
			'plate_well':plate_well,
			'mark':instance.hit,
			'hit_list':hit_list,
			'hit_prop':hit_prop,
			'plate':plate
			})

	def hits(self,request):
		"""
		return a list of hits on current plate 
		"""

		from library.models import compound, compound_serializer

		hit_list = [i['plate_well'] for i in hitlist.objects.filter(plate=self.curPlate).values('plate_well')]
		hit_list.sort(reverse=True)

		query = compound.objects.filter(plate_well__in=hit_list)
		serializer = compound_serializer(query,many=True)

		return hit_list, serializer.data #hit_list and data returned will not be the same. Some marked hit compound doesn't exists in library.


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

		if project.meta:#if there is meta data for this project. pass it to frontend.
			if 'map' in project.meta.keys():
				results['map'] = project.meta['map'] 

		return Response(results)

	@detail_route(methods=['POST'])
	def parse(self,request,pk=None): #The function to parse list csv file to database
		"""
		take the list file and convert it to a format that can be used by front end.
		"""

		def file2dict(csvfile,plates,readouts):
			"""
			convert a list file to a dict that has platewell as key. Readouts are arrays.
			"""
			import csv

			sample = csvfile.read(1024)
			csvfile.seek(0)

			dialect = csv.Sniffer().sniff(sample)
			reader = csv.DictReader(csvfile, dialect=dialect)

			content = {}

			for row in reader:

				plateNum = plates[row['plate']]
				wellNum = row['well']

				if (plateNum+wellNum) in content.keys():
					#if there are duplicate readouts combine them into array
					for k,v in readouts.iteritems():
						content[plateNum+wellNum][v] += [row[k]]

				else:

					content[plateNum+wellNum] = {
						'plate':plateNum,
						'well':wellNum,
					}

					for k,v in readouts.iteritems():
						content[plateNum+wellNum][v] = [row[k]]

			return content

		def dict2object(d,project,readouts):
			"""
			convert a dict that has platewell as key, to data objects that can be parsed into database
			in the mean time create meta data for this data
			"""
			l = []
			fields = []
			for k,v in d.iteritems():

				counter = 1
				
				dataDict = {
					'library': 'ICCB',
					'project': project,
					'plate_well': k,
					'plate': v['plate'],
					'well': v['well']
				}
				
				for r in readouts.values():
					
					for i,item in enumerate(v[r]):
						if [x for x in fields if x['name'] == 'readout' + str(counter)] == []:
							fields.append({
								'name':'readout'+str(counter),
								'verbose':r + str(i+1),
								'datatype':'numeric',
								})

						dataDict['readout'+str(counter)] = item
						counter += 1

				l.append(data(**dataDict))

			return l,{'fields':fields,
						'map':readouts}



		file_instance = get_object_or_404(csv_file,pk=pk)

		project =find_or_create_project(request)

		d = request.POST


		plates = odict()
		readouts = odict()

		for i,item in enumerate(d.getlist('oreadouts[]')):
			if d.getlist('readouts[]')[i]:
				readouts[item] = d.getlist('readouts[]')[i]


		for i,item in enumerate(d.getlist('oplates[]')):
			plates[item] = d.getlist('plates[]')[i]

		f = file_instance.cleaned_csv_file
		f.open(mode='rb')

		#check if plate already exists in database if so delete
		data.objects.filter(plate__in=set(plates.values())).delete()

		dataList, meta = dict2object(file2dict(f,plates,readouts),project,readouts)

		meta['positives'] = d.getlist('positives[]')
		meta['negatives'] = d.getlist('negatives[]')

		#bulk create data. This is much faster than 1 by 1
		data.objects.bulk_create(dataList)

		#set controls

		all_parsed_data = data.objects.filter(plate__in=set(plates.values()))
		all_parsed_data.filter(well__in=meta['positives']).update(welltype='P')
		all_parsed_data.filter(well__in=meta['negatives']).update(welltype='N')

		#update the meta data of this project
		project.meta = meta
		project.save()

		return Response("parsed")
	
	def perform_create(self,serializer): #called when upload a file
		
		serializer.save(project=find_or_create_project(self.request))

