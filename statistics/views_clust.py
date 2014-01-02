from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
#from django.core.paginator import Paginator
#from django.core.context_processors import csrf
#from django.contrib import messages
from django.db.models import Count

#from collections import OrderedDict as od

from library.models import compound

import statistics.plot_statistics as stat
import statistics.plot_cluster as clust
from process.forms import PlatesToUpdate

#=============================================================================
## facilitate functions    

def _select_plates(request):
#    form=PlatesToUpdate()
    if not 'proj' in request.session:
        return render(request,"main/error.html",{'error_msg':"No project specified!"})   
        
    exec ('from data.models import proj_'+request.session['proj_id']+' as data')
        ## Retrive data to be ploted
    plates=list()
    for i in list(data.objects.values('plate').annotate(x=Count('plate'))):
        plates.append(i['plate'])
    plates=sorted(plates)    

    if request.POST.get('plates'):
        plates_selected=request.POST.get('plates').split(',')
        
    else:
        plates_selected = []   

    if request.POST.get('data_column_to_plot'):
        data_columns=request.POST.get('data_column_to_plot').split(',')        
    else:
        data_columns = []

    field_list = []
    for i in data._meta.fields:
        if i.name not in "id library library_pointer_id compound_pointer_id plate well platewell ishit welltype project submission create_date create_by":
            field_list.append(i.name)    

    return [plates,plates_selected,data,field_list,data_columns]


def _cmap_list():
    cmaps = [('Sequential',     ['binary', 'Blues', 'BuGn', 'BuPu', 'gist_yarg',
                             'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                             'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                             'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd']),
         ('Sequential (2)', ['afmhot', 'autumn', 'bone', 'cool', 'copper',
                             'gist_gray', 'gist_heat', 'gray', 'hot', 'pink',
                             'spring', 'summer', 'winter']),
         ('Diverging',      ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                             'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'seismic']),
         ('Qualitative',    ['Accent', 'Dark2', 'hsv', 'Paired', 'Pastel1',
                             'Pastel2', 'Set1', 'Set2', 'Set3', 'spectral']),
         ('Miscellaneous',  ['gist_earth', 'gist_ncar', 'gist_rainbow',
                             'gist_stern', 'jet', 'brg', 'CMRmap', 'cubehelix',
                             'gnuplot', 'gnuplot2', 'ocean', 'rainbow',
                             'terrain', 'flag', 'prism'])]
    cmap_list = ['jet', 'brg', 'CMRmap', 'cubehelix',
                 'gnuplot', 'gnuplot2', 'ocean', 'rainbow',
                 'terrain', 'flag', 'prism','BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'seismic' ]
    return cmap_list
#=============================================================================
## stable views for cluster analysis

def heatmap(request):
    """ basic function to plot heatmaps 
    """
    ### This function is still in the testing phase
    ### because one plate seems like have more than 384 wells...
  
    plates,plates_selected,data,field_list,data_columns =_select_plates(request)
    form=PlatesToUpdate()    
    img_list = []  
    cmap_list = _cmap_list()

    if request.POST.get('heatmap_color'):
        cmap=request.POST.get('heatmap_color')
    else:
        cmap = 'jet'
    
   
    for plate_number in plates_selected:    
        entry_list = data.objects.filter(plate = plate_number if plate_number.isdigit() else plate_number[:-1])
        
        for data_column in data_columns:
            well_list = []
            plate_well_list = []
            fp_list = []    
            for e in entry_list:
                well_list.append(e.well)
                fp_list.append(float(getattr(e,data_column)))
                plate_well_list.append(plate_number+'_'+e.well)
            
            ## Plot Heat maps        
            c = stat.plot_heatmap(well_list, fp_list,plate_well_list,cmap=cmap,plate_number = (plate_number+' '+data_column))             
            img_list.append(c)        

    url_name = 'stat_heatmap'
    return render(request,"statistics/plots.html",{'img_list':img_list,
                                                     'plates':plates,
                                                     'form':form,
                                                     'url_name':url_name,
                                                     'field_list':field_list,
                                                     'cmap_list':cmap_list
                                                     })  

#=============================================================================
## Stable compound views



#=============================================================================
## Testing views



def fingerprint_cluster(request):

    entry_list = compound.objects.filter(plate = '3266')#.filter(well = 'A05')
    fp2_list = []
    for entry in entry_list[:8]:
        fp2_list.append(entry.fp2)
    
#    c = cluster.test_hierarchical_cluster(fp2_list)
    c = cluster.test_networkx(fp2_list)
    
    return HttpResponse(c)     
    

#==============================================================================
### Old codes, used for backup, will be deleted
#import pylab
#import cStringIO
#def fig_out(format_out ='png'):
#    """ Write the output figure generated by pylab into a string that can be used in html\n
#    Default output format is PNG. \n
#    SVG format doesn't work yet. This function will be updated for svg output in the future    
#    """
#    sio = cStringIO.StringIO()
#    pylab.savefig(sio, format=format_out)
#    image_string = """<img src="data:image/png;base64,%s"/><br>""" % sio.getvalue().encode("base64").strip()
#    return image_string

#def backup_heatmap(request):
#    """ basic function to plot heatmaps for plate replicates\
#        can expand to plot many different statistics    
#    """
#    ### This function is still in the testing phase
#    ### because one plate seems like have more than 384 wells...
#    if 'proj' in request.session: 
#        exec ('from data.models import proj_'+request.session['proj_id']+' as data')
#        ## Retrive data to be ploted
#        plate_number = '2'        
#        entry_list = data.objects.filter(plate = plate_number)
#        
#        replicate_dic = {}       
#        for e in entry_list:
#            if e.replicate not in replicate_dic.keys():
#                well = []
#                fp = []
#                replicate_dic.update({e.replicate:[well,fp]})
#                replicate_dic[e.replicate][0].append(e.well)
#                replicate_dic[e.replicate][1].append(float(e.FP))
#            else:
#                replicate_dic[e.replicate][0].append(e.well)
#                replicate_dic[e.replicate][1].append(float(e.FP))
#
#        ## Plot Heat maps
#        img_strings = ''
#        for k in replicate_dic.keys():
#            well_list = replicate_dic[k][0]
#            fp_list = replicate_dic[k][1]            
#            img_strings += stat.plot_interactive_heatmap(well_list, fp_list,plate_number = (plate_number+k))     
#        
#        ## Plot Reproductivity   
#        ## This plot might have bug if A and B doesn't have same well number
#        ## This will be addressed in the future
#        img_strings += stat.plot_linearfit(replicate_dic['A'][1],replicate_dic['B'][1], (plate_number+'A'),(plate_number+'B'))
#
#        ## Plot Histogram
#        img_strings += stat.plot_histogram((replicate_dic['A'][1]+replicate_dic['B'][1]))
#        
#        ##Plot cluster
#        c = stat.test_cluster(replicate_dic['A'][1])   
#        
#        ## plot cluster
##        c= stat.test_hierarchical_cluster()
#        
#        
#        return HttpResponse(img_strings)        
#
#    else:
#        return render(request,"main/data_list.html",{}) ## return address need to be re-defined            





#def compound_list(request):
#    """ display list of compounds \n
#    This function is supposed to be used by users to select a few compounds \n
#    And it will return this table as summary    
#    """
#    entry_list = compound.objects.filter(plate = '3266')
#    field_list = []
#    for i in compound._meta.fields:
#        if i.name not in 'pubchem_cid id fp2 fp3 fp4 sdf plate well canonical_smiles inchi molecular_weight formula':            
#            field_list.append((i.name))
#    
#    current_page = (request.GET.get('page'))
#        
#    p = Paginator(entry_list,30)    
#    
#    if not current_page:
#        current_page=1   
#   
#    if p.num_pages <=7:
#        page_range = range(1,(p.num_pages+1))        
#    elif int(current_page)+3 >= p.num_pages:
#        page_range = range(p.num_pages - 7, p.num_pages)
#    else:
#        page_range = range(max(1,int(current_page)-3),max(1,int(current_page)-3)+7) 
#        
#
#    return render(request, "statistics/compounds.html",{'entry_list': p.page(current_page),
#                                                  'field_list': field_list,
#                                                  'pages': page_range,
#                                                  'last_page':p.num_pages
#                                                })    
     
