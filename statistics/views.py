from django.shortcuts import render
from django.http import HttpResponse


from library.models import compound
import pylab
import cStringIO


def index(request):
    return render(request, "statistics/index.html")

def plot(request):
    """Plot data dynamically on the page
    """
    query1 = compound.objects.all()
    y1 = []
    for q in query1:
        y1.append(q.molecular_weight)        
    pylab.title('Scatter_plot')
    pylab.xlabel('test_xlabel')
    pylab.ylabel('test_ylabel')    
    pylab.plot(y1, 'ro', label='group1')
    
    
    format = "png"
    sio = cStringIO.StringIO()
    pylab.savefig(sio, format=format)
    c = """<img src="data:image/png;base64,%s"/>""" % sio.getvalue().encode("base64").strip()
    
    
    return HttpResponse(c)
    
