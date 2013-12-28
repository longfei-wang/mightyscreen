from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from django.core.paginator import Paginator
from django.core.context_processors import csrf
from django.contrib import messages

from collections import OrderedDict as od

from library.models import compound
from main.models import project, data_base
import pylab
import cStringIO

import statistics.plot_statistics as stat

#=============================================================================
## facilitate functions
def fig_out(format_out ='png'):
    """ Write the output figure generated by pylab into a string that can be used in html\n
    Default output format is PNG. \n
    SVG format doesn't work yet. This function will be updated for svg output in the future    
    """
    sio = cStringIO.StringIO()
    pylab.savefig(sio, format=format_out)
    image_string = """<img src="data:image/png;base64,%s"/><br>""" % sio.getvalue().encode("base64").strip()
    return image_string
    


def index(request):
    return render(request, "statistics/index.html")

def plot(request):
    """Plot data dynamically on the page
    This is a test page for ther
    """
    query1 = compound.objects.all().filter(plate = '3265')
    y1 = []
    for q in query1:
        y1.append(q.molecular_weight)        
    pylab.title('Scatter_plot')
    pylab.xlabel('test_xlabel')
    pylab.ylabel('test_ylabel')    
    pylab.plot(y1, 'ro', label='group1')

    c = fig_out()    
    
    return HttpResponse(c)

def compound_list(request):
    """ display list of compounds \n
    This function is supposed to be used by users to select a few compounds \n
    And it will return this table as summary    
    """
    entry_list = compound.objects.filter(plate = '3266')
    field_list = []
    for i in compound._meta.fields:
        if i.name not in 'pubchem_cid id fp2 fp3 fp4 sdf plate well canonical_smiles inchi molecular_weight formula':            
            field_list.append((i.name))
    
    current_page = (request.GET.get('page'))
        
    p = Paginator(entry_list,30)    
    
    if not current_page:
        current_page=1   
   
    if p.num_pages <=7:
        page_range = range(1,(p.num_pages+1))        
    elif int(current_page)+3 >= p.num_pages:
        page_range = range(p.num_pages - 7, p.num_pages)
    else:
        page_range = range(max(1,int(current_page)-3),max(1,int(current_page)-3)+7) 
        

    return render(request, "statistics/compounds.html",{'entry_list': p.page(current_page),
                                                  'field_list': field_list,
                                                  'pages': page_range,
                                                  'last_page':p.num_pages
                                                })    
     
def details(request):
    """ display detailed information of compounds, use list"""
    try:
        cmpd = compound.objects.get(plate = request.GET.get('plate'),well=request.GET.get('well'))
    except:
        cmpd= False
    field_list="chemical_name molecular_weight formula library_name facility_reagent_id plate well pubchem_id tpsa logp inchikey canonical_smiles".split()
    if request.GET.get('t'):#if t then show as tooltip
        return render(request, "statistics/detail_tooltip.html", {'cmpd': cmpd,'field_list':field_list})    
    return render(request, "statistics/details.html", {'cmpd': cmpd,'field_list':field_list})

def heatmap(request):
    """ basic function to plot heatmaps for plate replicates\
        can expand to plot many different statistics    
    """
    ### This function is still in the testing phase
    ### because one plate seems like have more than 384 wells...
    if 'proj' in request.session: 
        exec ('from data.models import proj_'+request.session['proj_id']+' as data')
        ## Retrive data to be ploted
        plate_number = '2'        
        entry_list = data.objects.filter(plate = plate_number)
        
        replicate_dic = {}       
        for e in entry_list:
            if e.replicate not in replicate_dic.keys():
                well = []
                fp = []
                replicate_dic.update({e.replicate:[well,fp]})
                replicate_dic[e.replicate][0].append(e.well)
                replicate_dic[e.replicate][1].append(float(e.FP))
            else:
                replicate_dic[e.replicate][0].append(e.well)
                replicate_dic[e.replicate][1].append(float(e.FP))

        ## Plot Heat maps
        img_strings = ''
        for k in replicate_dic.keys():
            well_list = replicate_dic[k][0]
            fp_list = replicate_dic[k][1]            
            img_strings += stat.plot_interactive_heatmap(well_list, fp_list,plate_number = (plate_number+k))     
        
        ## Plot Reproductivity   
        ## This plot might have bug if A and B doesn't have same well number
        ## This will be addressed in the future
        img_strings += stat.plot_linearfit(replicate_dic['A'][1],replicate_dic['B'][1], (plate_number+'A'),(plate_number+'B'))

        ## Plot Histogram
        img_strings += stat.plot_histogram((replicate_dic['A'][1]+replicate_dic['B'][1]))
        
        ##Plot cluster
        c = stat.test_cluster(replicate_dic['A'][1])   
        
        ## plot cluster
#        c= stat.test_hierarchical_cluster()
        
        
        return HttpResponse(img_strings)        

    else:
        return render(request,"main/data_list.html",{}) ## return address need to be re-defined

def interactive_heatmap(request):
    """ basic function to plot heatmaps for plate replicates\
        can expand to plot many different statistics    
    """
    ### This function is still in the testing phase
    ### because one plate seems like have more than 384 wells...
    if 'proj' in request.session: 
        exec ('from data.models import proj_'+request.session['proj_id']+' as data')
        ## Retrive data to be ploted
        plate_number = '2'        
        entry_list = data.objects.filter(plate = plate_number)
        
        replicate_dic = {}       
        for e in entry_list:
            if e.replicate not in replicate_dic.keys():
                well = []
                fp = []
                replicate_dic.update({e.replicate:[well,fp]})
                replicate_dic[e.replicate][0].append(e.well)
                replicate_dic[e.replicate][1].append(float(e.FP))
            else:
                replicate_dic[e.replicate][0].append(e.well)
                replicate_dic[e.replicate][1].append(float(e.FP))

        ## Plot Heat maps
        img_strings = ''
        for k in replicate_dic.keys():
            well_list = replicate_dic[k][0]
            fp_list = replicate_dic[k][1]            
            c = stat.plot_interactive_heatmap(well_list, fp_list,plate_number = (plate_number+k))     
        
        
        return HttpResponse(c)        

    else:
        return render(request,"main/data_list.html",{}) ## return address need to be re-defined


#=============================================================================
## Testing views

import statistics.clustering as cluster

def fingerprint_cluster(request):

    entry_list = compound.objects.filter(plate = '3266')#.filter(well = 'A05')
    fp2_list = []
    for entry in entry_list:
        fp2_list.append(entry.fp2)
    
    c = cluster.test_hierarchical_cluster(fp2_list)
#    c = cluster.test_MDS(fp2_list)
    
    return HttpResponse(c)     
    

            