from django.core.cache import cache
from math import *
import re
import numpy as np

class ScoreReader():
	"""a class that parse the scores from user's formular"""
	def __init__(self,proj,data):
		self.data=data
		self.proj=proj
		self.readout=proj.readout.all()
		self.rep=self.proj.rep()
		self.dict={#except from col and rep name all should be lowercase
		'neg':'N',
		'pos':'P',
		'com':'X',
		}
		self.whitelist=['acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'ceil', 'copysign', 'cos', 'cosh', 'degrees', 'e', 'erf', 'erfc', 'exp', 'expm1', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'hypot', 'isinf', 'isnan', 'ldexp', 'lgamma', 'log', 'log10', 'log1p', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'trunc','abs','if','else','in','and','or','not']

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

	def cal(self,values,f,axis=None):
		map={'std':'np.std',
		'avg':'np.average',
		'min':'np.amin',
		'max':'np.amax',
		'sum':'np.sum',
		'count':'np.size',
		'var':'np.var'}
		if f in map:
			return eval('%s(values,axis)'%map[f])
		else:
			raise Exception("Unkown Function:%s"%f)

	def parse(self,curRow,formular='{FP_A}'):#parse user's formular 
		curPlate=curRow.plate
		curWell=curRow.well
		var=re.findall('{[^}]+}',formular)	

		data=self.data

		for i in var:

			j=i.strip('{}').split('.')
			if len(j) > 2:
				if j[2] in 'pos neg com':#constants related to controls and all compounds on one plate


					if self.fetch(i.strip('{}')):#check if already in cache
						var=self.fetch(i.strip('{}'))
					else:#otherwise calculate

						result=data.objects.filter(plate=curPlate,welltype=self.dict[j[2]]).only('readout')
						
						if not result:#if no result found then no pos or neg
							raise Exception('There is no Positive/Negative wells marked on plate:%s'%curPlate)

						values=list()#first make a 2 dimension array. row*rep
						for m in result:
							if j[0] in m.readout:
								values.append(m.readout[j[0]])

						if j[1] == 'all':#all replicates

							var=self.cal(values,j[3])

						else:
						
							if self.proj.rep_namespace.index(j[1]):
								var=self.cal(values,j[3],0)[self.proj.rep_namespace.index(j[1])]
							else:
								raise Exception("Unkown replicate")							
						
						self.save(i.strip('{}'),str(var))
				
				else:
					if j[1] == 'all' and j[0] in curRow.readout:#all replicates
						var=self.cal(curRow.readout[j[0]],j[2])
					else:
						raise Exception("Unkown replicate/function")

			else:#just refer to row
				if hasattr(curRow,i.strip('{}')):
					var=getattr(curRow,i.strip('{}'))
				elif hasattr(curRow,j[0]+'_'+j[1]):
					var=getattr(curRow,j[0]+'_'+j[1])
			
			formular=formular.replace(i,str(var)) if var else formular#this need to be float
			
		if re.findall('{[^}]+}',formular):
			raise Exception('Unsupported Variables:%s'%', '.join(re.findall('{[^}]+}',formular)))


		if [i for i in re.findall("\w(?<!\d)[\w'-]*",formular) if i not in self.whitelist and len(i)>1 ]:#if words not in whitelist then rasise error and stop, secure enough?
			raise Exception('Unsupported Function')

		val=eval(formular)

		return val
