from django.db import connection
from django.core.cache import cache
from math import *
import re

class ScoreReader():
	"""a class that parse the scores from user's formular"""
	def __init__(self,proj):
		self.proj=proj
		self.readout=proj.experiment.readout.all()
		self.rep=self.proj.rep()
		self.dict={#except from col and rep name all should be lowercase
		'neg':'N',
		'pos':'P',
		'com':'X',
		'sd':'STDDEV_SAMP',
		'avg':'AVG',
		'min':'MIN',
		'max':'MAX',
		'count':'COUNT',
		'sum':'SUM',
		'var':'VAR_SAMP'
		}
		self.whitelist=['acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'e', 'erf', 'erfc', 'exp', 'expm1', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'hypot', 'isinf', 'isnan', 'ldexp', 'lgamma', 'log', 'log10', 'log1p', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'trunc','abs','if','else','in']

	def save(self,key,value):#cache result
		c=dict()  
		if cache.get('ScoreReader'):
			c=cache.get('ScoreReader')
		c.update({key:value})
		cache.set('ScoreReader',c)

	
	def fetch(self,key):#read cache result
		c=dict()
		if cache.get('ScoreReader'):
			c=cache.get('ScoreReader')
		if key in c.keys():
			return c[key]
		else:
			return False

	def flush(self):#flush all cache, should do this when changing plate
		cache.set('ScoreReader',None)

	def parse(self,curRow,formular='{FP_A}',mysql=False):#parse user's formular 
		curPlate=curRow.plate
		curWell=curRow.well
		var=re.findall('{[^}]+}',formular)
		cursor = connection.cursor()
		col_quote= '' if mysql == True else '"'		
		row=[0]

		for i in var:

			j=i.strip('{}').split('.')
			if len(j) > 2:
				if j[2] in 'pos neg com':#constants related to controls and all compounds on one plate


					if self.fetch(i.strip('{}')):#check if already in cache
						row=[self.fetch(i.strip('{}'))]
					else:#otherwise calculate
						if j[1] == 'all':#all replicates
							arg=list()
							for x in self.rep:
								arg.append("""(SELECT %(quote)s%(col)s_%(rep)s%(quote)s AS VAL FROM data_proj_%(proj_id)s WHERE plate='%(plate)s' and welltype='%(welltype)s')"""%{
								               'quote':col_quote,
								               'proj_id':self.proj.pk,
								               'col':j[0],
								               'rep':x,
								               'plate':curPlate,
								               'welltype':self.dict[j[2]]})

							query=" UNION ALL ".join(arg)
							cursor.execute("""SELECT %(f)s(VAL) FROM (%(query)s) as subquery"""%{'f':self.dict[j[3]],'query':query})
							row = cursor.fetchone()

						else:
							query="""SELECT %(f)s(%(quote)s%(col)s_%(rep)s%(quote)s) FROM data_proj_%(proj_id)s WHERE plate='%(plate)s' and welltype='%(welltype)s'"""%{
									'quote':col_quote,
									'proj_id':self.proj.pk,
									'col':j[0],
									'rep':j[1],
									'plate':curPlate,
									'welltype':self.dict[j[2]],
									'f':self.dict[j[3]]}
							
							cursor.execute(query)
							row = cursor.fetchone()

						if not row[0]: 
							raise Exception('There is no Positive or Negative wells marked on plate:%s'%curPlate)
						
						self.save(i.strip('{}'),str(row[0]))
				
				elif j[2] in 'sd avg min max count sum var':#variable for one row
					if j[1] == 'all':#all replicates
						arg=list()
						for x in self.rep:
							arg.append("""(SELECT %(quote)s%(col)s_%(rep)s%(quote)s AS VAL FROM data_proj_%(proj_id)s WHERE plate='%(plate)s' and well='%(well)s')"""%{
										   'quote':col_quote,
										   'proj_id':self.proj.pk,
										   'col':j[0],'rep':x,
										   'plate':curPlate,
										   'well':curWell})
						
						query=" UNION ALL ".join(arg)
						cursor.execute("""SELECT %(f)s(VAL) FROM (%(query)s) as subquery"""%{'f':self.dict[j[2]],'query':query})
						row = cursor.fetchone()
			else:#just refer to row
				if hasattr(curRow,i.strip('{}')):
					row=[getattr(curRow,i.strip('{}'))]
			
			formular=formular.replace(i,str(row[0])) if row[0] else formular#this need to be float
			
		if re.findall('{[^}]+}',formular):
			raise Exception('Unsupported Variables:%s'%', '.join(re.findall('{[^}]+}',formular)))


		if [i for i in re.findall("\w(?<!\d)[\w'-]*",formular) if i not in self.whitelist and len(i)>1 ]:#if words not in whitelist then rasise error and stop, secure enough?
			raise Exception('Unsupported Function')

		val=eval(formular)

		return val