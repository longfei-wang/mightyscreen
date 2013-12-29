from django.db import transaction
import csv
from django.db.models.loading import get_model


@transaction.commit_manually
def flush_transaction():
    """
    Flush the current transaction so we don't read stale data

    Use in long running processes to make sure fresh data is read from
    the database.  This is a problem with MySQL and the default
    transaction mode.  You can fix it by setting
    "transaction-isolation = READ-COMMITTED" in my.cnf or by calling
    this function at the appropriate moment
    """
    transaction.commit()




def dump2csv(qs, outfile_path):
	"""
	Takes in a Django queryset and spits out a CSV file.
	
	Usage::
	
		>> from utils import dump2csv
		>> from dummy_app.models import *
		>> qs = DummyModel.objects.all()
		>> dump2csv.dump(qs, './data/dump.csv')
	
	Based on a snippet by zbyte64::
		
		http://www.djangosnippets.org/snippets/790/
	
	"""
	model = qs.model
	writer = csv.writer(open(outfile_path, 'w'))
	
	headers = []
	for field in model._meta.fields:
		headers.append(field.name)
	writer.writerow(headers)
	
	for obj in qs:
		row = []
		for field in headers:
			val = getattr(obj, field)
			if callable(val):
				val = val()
			if type(val) == unicode:
				val = val.encode("utf-8")
			row.append(val)
		writer.writerow(row)