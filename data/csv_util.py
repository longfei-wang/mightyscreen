#!/usr/bin/python
#
#
#A program to process the report file(grid view) from Envision reader/ICCB
#
#Longfei Wang
#

import csv
import sys
from collections import OrderedDict as odict



def read_csv_file(path,dictformat=False):
	"""
	csv reader wrapper
	"""

	with open(path, 'rU') as csvfile:

		sample = csvfile.read(1024)
		
		csvfile.seek(0)

		dialect = csv.Sniffer().sniff(sample)
		
		if dictformat:
			reader = csv.DictReader(csvfile, dialect=dialect)
		else:
			reader = csv.reader(csvfile, dialect=dialect)

		for row in reader:
			yield row


def checklist(inputfile=None):
	"""
	take a list file and output useful infos
	inputfiles is python file handler
	"""
	if inputfile==None: return {"failed":"inputfile is None"}

	titles = []
	plates = []
	cols = []
	rows = []

	reader = read_csv_file(inputfile)

	header = reader.next()
	
	numCol = len(header)

	plateIndex = header.index('plate')
	wellIndex = header.index('well')

	titles = [i for i in header if i not in "plate well plate_well hit welltype create_date".split()] #remove reserved name spaces

	line = 1

	for row in reader:
		
		line += 1

		if len(row) != numCol:
			return {"failed":"Bad CSV format",
					"header":header,
					"row":row,
					"line":line}

		if row[plateIndex] not in plates:
			plates.append(row[plateIndex])

		if row[wellIndex][-2:] not in cols:
			cols.append(row[wellIndex][-2:])

		if row[wellIndex][:-2] not in rows:
			rows.append(row[wellIndex][:-2])

	return {
		"plates":plates,
		"titles":titles,
		"cols":cols,
		"rows":rows,
		"numWells": len(rows)*len(cols),
		}


def file2dict(csvfile,plates,readouts,identifier):
	"""
	convert a list file to a dict that has platewell as key. Readouts are arrays.
	"""

	reader = read_csv_file(csvfile,dictformat=True)

	content = odict()

	for row in reader:

		plateNum = plates[row['plate']]
		wellNum = row['well']
		
		plate_well = str(plateNum)+str(wellNum)

		#######################################################
		#the core mapping for identifiers. (pubchem/rest/pug)
		#######################################################
		pubchem_header = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
		
		chem_id = "NA"


		if identifier:##### All supported chemical identifiers: pubchem link name cid smiles inchi inchikey formula ...

			if identifier.lower() == 'hms':
				chem_id = pubchem_header + 'name/HMS' + plate_well
			
			elif identifier.lower() == 'identifier':
				chem_id = row[identifier]

			elif identifier in row.keys() and identifier.lower() in "cid name smiles inchi sdf inchikey formula listkey".split():
				chem_id = pubchem_header + identifier.lower() +'/' + row[identifier]
			
				

		if plate_well in content.keys():
			#if there are duplicate readouts combine them into array
			for k in readouts:
				content[plate_well]['readouts'][k] += [row[k]]

		else:

			content[plate_well] = {
				'plate':plateNum,
				'well':wellNum,
				'hit': 0 if 'hit' not in row.keys() else row['hit'],
				'welltype': 'X' if 'welltype' not in row.keys() else row['welltype'].upper(),
				'identifier':chem_id,
				'readouts':odict(),
			}

			for k in readouts:
				content[plate_well]['readouts'][k] = [row[k]]


	return content
