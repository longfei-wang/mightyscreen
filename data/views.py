from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.response import Response
from django.core.files.base import ContentFile
from data.models import *
from data.grid2list import grid2list, checklist
import os
# Create your views here.

class DataViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
	"""
	populate data based on query
	"""
	queryset = data.objects.all()
	serializer_class = DataSerializer
	filter_class = DataFilter

	def get_queryset(self):
		p = get_object_or_404(project,id=self.request.session.get('project',None))
		return data.objects.filter(project=p)


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

		def dict2object(d,project):
			"""
			convert a dict that has platewell as key, to data objects
			"""
			l = []
			meta = {}
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
						if counter not in meta:
							meta[str(counter)] = r + str(i+1)
						dataDict['readout'+str(counter)] = item
						counter += 1

				l.append(data(**dataDict))

			return l,meta



		file_instance = get_object_or_404(csv_file,pk=pk)

		project =find_or_create_project(request)

		d = request.POST


		plates = {}
		readouts = {}
		

		for i,item in enumerate(d.getlist('oreadouts[]')):
			if d.getlist('readouts[]')[i]:
				readouts[item] = d.getlist('readouts[]')[i]


		for i,item in enumerate(d.getlist('oplates[]')):
			plates[item] = d.getlist('plates[]')[i]

		f = file_instance.cleaned_csv_file
		f.open(mode='rb')

		#check if plate already exists in database if so delete
		data.objects.filter(plate__in=set(plates.values())).delete()

		dataList, meta = dict2object(file2dict(f,plates,readouts),project)

		#bulk create data. This is much faster than 1 by 1
		data.objects.bulk_create(dataList)

		#update the meta data of this project
		project.meta = meta
		project.save()

		return Response("parse called")
	
	def perform_create(self,serializer): #called when upload a file
		
		serializer.save(project=find_or_create_project(self.request))

