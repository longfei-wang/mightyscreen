from models import compound,library 
from mongoengine import *

connect('mightyscreen')

com=compound()

com.plate='1133'
com.well='A01'
com.save()