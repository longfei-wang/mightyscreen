#!/usr/bin/python
#
#
#A program to process the report file(grid view) from Envision reader/ICCB
#
#Longfei Wang
#

import csv
import sys


class table():
	"""A class that handle tables in a grid file"""
	plates = list()
	titles = list()
	allcols = list()
	allrows = list()

	def __init__(self,pointer,plate_id,title,columns):
		self.columns = [i.zfill(2) for i in columns]
		self.plate_id = plate_id
		self.title = title

		self.rows=list()
		self.c=list()
		r = pointer.next()
		while r[0]:
			self.rows.append(r[0])
			self.c.append(r[1:])
			r = pointer.next()

		#maintain a list of unique plates cols rows and titles 
		self.allrows += [i for i in self.rows if i not in self.allrows]
		self.allcols += [i for i in self.columns if i not in self.allcols]
		if title not in self.titles:
			self.titles.append(title)
		if plate_id not in self.plates:
			self.plates.append(plate_id)

	def __getitem__(self,key):
		col = key[-2:]
		row = key[:-2]
		if col in self.columns and row in self.rows:
			try:
				return self.c[self.rows.index(row)][self.columns.index(col)]
			except:
				return ''

	@classmethod
	def wells(self):
		c = list()
		for row in self.allrows:
			for col in self.allcols:
				c.append(row+col)
		return c


def checklist(inputfile=None):
	"""
	take a list file and output useful infos
	inputfiles is python file handler
	"""
	if inputfile==None: return {"failed":"inputfile is None"}

	inputfile.seek(0)

	titles = []
	plates = []
	cols = []
	rows = []

	with inputfile as csvfile:

		sample = csvfile.read(1024)
		csvfile.seek(0)

		dialect = csv.Sniffer().sniff(sample)
		reader = csv.reader(csvfile, dialect)

		header = reader.next()
		numCol = len(header)

		plateIndex = header.index('plate')
		wellIndex = header.index('well')

		titles = [i for i in header if i not in "plate well".split()]

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


def test_all():
	i = open('grid.csv','rb')
	o = open('list.csv','w')
	print grid2list(i,o)
	i.close()
	o.close()
	f = open('list.csv','rb')
	print checklist(f)
	f.close()


def grid2list(inputfile=None,outputfile=None):
	"""
	take a grid file and output a list file
	both files are python file handlers
	"""
	if (inputfile==None or outputfile==None): return {"failed":"inputfile or outputfile is None"}

	inputfile.seek(0)
	outputfile.seek(0)

	plate_id = 0
	title = ''
	tabledict = dict()

	#print "Processing grid csv file....."

	with inputfile as csvfile:
		sample = csvfile.read(1024)
		csvfile.seek(0)

		if csv.Sniffer().has_header(sample):#check if this is a list file if so then return
			return {"is_list":True}

		dialect = csv.Sniffer().sniff(sample)
		
		reader = csv.reader(csvfile, dialect)

		for row in reader:#read through the grid csv file and find plates/talbes
			if row[0] == 'Plate':
				row = reader.next()

				try:
					plate_id = row[0]
					if plate_id not in tabledict.keys():
						tabledict[plate_id] = dict()
				except:
					pass

			elif ',1,2,3,4,5,6,7,8,9' in ','.join(row):#the columns header is the idenifier for a table, this might need to be improved
				if title:
					#print plate_id,title,reader.line_num
					tabledict[plate_id][title] = table(reader,plate_id,title,row[1:])

			else:
				title = ''.join(row)

	#print "Writing list csv file....."

	with outputfile as csvfile:
		writer=csv.writer(csvfile,delimiter=',')

		writer.writerow(['plate','well']+table.titles)#header
		
		for plate in table.plates:
			for well in table.wells():

				#print plate,well,

				line = list()

				line+=[plate,well]

				for title in table.titles:
					try:
						line.append(tabledict[plate][title][well])
					except:
						line.append('None')

				writer.writerow(line)


	#print "Done!"
	return {
		"plates":table.plates,
		"titles":table.titles,
		"cols":table.allcols,
		"rows":table.allrows,
		"numWells": len(table.allcols)*len(table.allrows),
		}