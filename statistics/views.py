from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
#from django.core.paginator import Paginator
#from django.core.context_processors import csrf
#from django.contrib import messages
from django.db.models import Count
from django.contrib import messages
#from collections import OrderedDict as od

from library.models import compound

from main.views import view_class
import statistics.plot_statistics as stat
import statistics.plot_cluster as clust
from process.forms import PlatesToUpdate

#=============================================================================
## facilitate functions    
class view_stat_class(view_class):
    """basic view class for stats"""
    def _select_plates(self,request):
    #    form=PlatesToUpdate()
        plates=self.plates
        data=self.data

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

        return [plates,plates_selected,self.data,field_list,data_columns]


    def _cmap_list(self):
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

    def _dendro_para(self,request):
        d_xy = []
        m_xy = []
        for a in 'xy':    
            if request.POST.get(('dendro_color_by_'+a)):
                value=request.POST.get(('dendro_color_by_'+a))
                if value == 'similarity':
                    if request.POST.get(('dendro_color_value_similarity_'+a)):
                        similarity=float(request.POST.get(('dendro_color_value_similarity_'+a))) ### some bug here
                        distance = 1 -similarity
                        d_xy.append(distance)
                    else:
                        distance = 0.9 ## default value 
                        d_xy.append(distance)
        
                elif value == 'bin':
                    if request.POST.get(('dendro_color_value_bin_'+a)):
                        distance=int(request.POST.get(('dendro_color_value_bin_'+a))) 
                        d_xy.append(distance)
                    else:
                        distance = 2 ## default value, use distance to pass bin number into the function  
                        d_xy.append(distance)
            
            else:
                distance = 0.9 ## default color by distance 0.9
                d_xy.append(distance)
                
            if request.POST.get(('linkage_method_'+a)):
                method = request.POST.get(('linkage_method_'+a))
                m_xy.append(method)
            else:
                method = 'complete'
                m_xy.append(method) 
                
        return d_xy[0],m_xy[0],d_xy[1],m_xy[1]
    
#=============================================================================
## stable views for plate analysis


class details(view_class):
    def c(self,request):

        """ display detailed information of compounds, use list"""
        try:
            cmpd = compound.objects.get(plate = request.GET.get('plate'),well=request.GET.get('well'))
        except:
            cmpd= False
        field_list="chemical_name molecular_weight formula library_name facility_reagent_id plate well pubchem_id tpsa logp inchikey canonical_smiles".split()
        if request.GET.get('t'):#if t then show as tooltip
            return render(request, "statistics/detail_tooltip.html", {'cmpd': cmpd,'field_list':field_list})    
        return render(request, "statistics/details.html", {'cmpd': cmpd,'field_list':field_list})



class heatmap(view_stat_class):
    def c(self,request):
        """ basic function to plot heatmaps 
        """
        ### This function is still in the testing phase
      
        plates,plates_selected,data,field_list,data_columns =self._select_plates(request)
        form=PlatesToUpdate()    
        img_list = []  
        cmap_list = self._cmap_list()

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

class correlation(view_stat_class):
    def c(self,request):
        """ basic function to plot heatmaps 
        """
        ### This function is still in the testing phase
        ### because one plate seems like have more than 384 wells...
        plates, plates_selected,data,field_list,data_columns =self._select_plates(request)
        form=PlatesToUpdate()    
        img_list = []  

        if request.POST.get('all_plates'):
            value=request.POST.get('all_plates')
            all_plates =True if value =="default" else False
        else:
            all_plates =True
        


        if len(data_columns)>1:
            if all_plates == False:
                for plate_number in plates_selected:    
                    entry_list = data.objects.filter(plate = plate_number if plate_number.isdigit() else plate_number[:-1])
                    correlation_list = []
                    for data_column in data_columns:
                        well_list = []
                        plate_well_list = []
                        fp_list = []
                        well_type_list = []
                        for e in entry_list:
                            well_list.append(e.well)
                            fp_list.append(float(getattr(e,data_column)))
                            plate_well_list.append(plate_number+'_'+e.well)
                            well_type_list.append(e.welltype)
                        correlation_list.append(fp_list)
                    ## Plot Reproductivity   
                    ## This plot might have bug if A and B doesn't have same well number
                    ## This will be addressed in the future
                    label_x = data_columns[0]
                    label_y = data_columns[1]
                    c = stat.plot_linearfit(correlation_list[0],correlation_list[1], plate_well_list, plate_number,well_type_list,label_x,label_y)
                    img_list.append(c)                                     
                
            elif all_plates == True:
                correlation_list = []
                for data_column in data_columns:                                    
                    well_list = []
                    plate_well_list = []
                    fp_list = []
                    well_type_list = []
                    #for plate_number in plates_selected:
                    entry_list = data.objects.filter(plate__in = plates_selected)
                    #raise Exception([x['FP_A'] for x in entry_list.values('plate','well','welltype','FP_A')])
                    for e in entry_list:
                        well_list.append(e.well)
                        fp_list.append(float(getattr(e,data_column)))
                        plate_well_list.append(e.plate+'_'+e.well)
                        well_type_list.append(e.welltype)
                    correlation_list.append(fp_list)
                    ## Plot Reproductivity   
                    ## This plot might have bug if A and B doesn't have same well number
                    ## This will be addressed in the future
                    label_x = data_columns[0]
                    label_y = data_columns[1]
                plate_number = (', ').join(map(str, plates_selected))
                c = stat.plot_linearfit(correlation_list[0],correlation_list[1], plate_well_list, plate_number,well_type_list,label_x,label_y)
                img_list.append(c) 
        
        
        elif len(data_columns)==1:
            img_list.append("Please select more than one parameters for correlation calculation")              
                


        url_name = 'stat_correlation'
        return render(request,"statistics/plots.html",{'img_list':img_list,
                                                         'plates':plates,
                                                         'form':form,
                                                         'url_name':url_name,
                                                         'field_list':field_list,
                                                         })  
                                                                                                       
                                                                                                         
class scatter(view_stat_class):
    def c(self,request):
        """ basic function to plot heatmaps 
        """
        ### This function is still in the testing phase
        ### because one plate seems like have more than 384 wells...
        plates, plates_selected,data,field_list,data_columns =self._select_plates(request)
        form=PlatesToUpdate()    
        img_list = [] 
        
        if request.POST.get('all_plates'):
            value=request.POST.get('all_plates')
            all_plates =True if value =="default" else False
        else:
            all_plates =True

        if request.POST.get('sort_value'):
            sort=request.POST.get('sort_value')
        else:
            sort = "default"    
        
        
        if all_plates == False:        
            for plate_number in plates_selected:    
                entry_list = data.objects.filter(plate = plate_number if plate_number.isdigit() else plate_number[:-1])     
                for data_column in data_columns:
                    well_list = []
                    plate_well_list = []
                    fp_list = []
                    well_type_list = []
                    for e in entry_list:
                        well_list.append(e.well)
                        fp_list.append(float(getattr(e,data_column)))
                        plate_well_list.append(plate_number+'_'+e.well)
                        well_type_list.append(e.welltype)
        
                ## Plot Reproductivity   
                ## This plot might have bug if A and B doesn't have same well number
                ## This will be addressed in the future
                    c = stat.plot_scatter(fp_list, plate_well_list,well_type_list,plate_number = (plate_number+' '+data_column), sort = sort)
                    img_list.append(c)        

        if all_plates == True:        
            for data_column in data_columns:
                well_list = []
                plate_well_list = []
                fp_list = []
                well_type_list = []
                for plate_number in plates_selected:    
                    entry_list = data.objects.filter(plate = plate_number if plate_number.isdigit() else plate_number[:-1])                 
                    for e in entry_list:
                        well_list.append(e.well)
                        fp_list.append(float(getattr(e,data_column)))
                        plate_well_list.append(plate_number+'_'+e.well)
                        well_type_list.append(e.welltype)
        
                ## Plot Reproductivity   
                ## This plot might have bug if A and B doesn't have same well number
                ## This will be addressed in the future
                plate_number = (', ').join(map(str, plates_selected))
                c = stat.plot_scatter(fp_list, plate_well_list,well_type_list,plate_number = (plate_number+' '+data_column),sort = sort)
                img_list.append(c)  

        url_name = 'stat_scatter'
        return render(request,"statistics/plots.html",{'img_list':img_list,
                                                         'plates':plates,
                                                         'form':form,
                                                         'url_name':url_name,
                                                         'field_list':field_list,
                                                         })  
                                                        

class histogram(view_stat_class):
    def c(self,request):
        """ basic function to plot histogram 
        """
        ### This function is still in the testing phase
        ### because one plate seems like have more than 384 wells...
        plates, plates_selected,data,field_list,data_columns =self._select_plates(request)
        form=PlatesToUpdate()    
        img_list = [] 
        all_plates =True

        if all_plates == False:        
            for plate_number in plates_selected:    
                entry_list = data.objects.filter(plate = plate_number)     
                for data_column in data_columns:
                    well_list = []
                    plate_well_list = []
                    fp_list = []
                    well_type_list = []
                    for e in entry_list:
    #                    well_list.append(e.well)
                        fp_list.append(float(getattr(e,data_column)))
    #                    plate_well_list.append(plate_number+'_'+e.well)
    #                    well_type_list.append(e.welltype)
        
                ## Plot Reproductivity   
                ## This plot might have bug if A and B doesn't have same well number
                ## This will be addressed in the future
                    c = stat.plot_histogram(fp_list, plate_number = (plate_number+' '+data_column),)
                    img_list.append(c)        

        if all_plates == True:        
            for data_column in data_columns:
                well_list = []
                plate_well_list = []
                fp_list = []
                well_type_list = []
                for plate_number in plates_selected:    
                    entry_list = data.objects.filter(plate = plate_number)                 
                    for e in entry_list:
    #                    well_list.append(e.well)
                        fp_list.append(float(getattr(e,data_column)))
    #                    plate_well_list.append(plate_number+'_'+e.well)
    #                    well_type_list.append(e.welltype)
        
                ## Plot Reproductivity   
                ## This plot might have bug if A and B doesn't have same well number
                ## This will be addressed in the future
                plate_number = (', ').join(map(str, plates_selected))
                c = stat.plot_histogram(fp_list,plate_number = (plate_number+' '+data_column),)
                img_list.append(c)  



        url_name = 'stat_histogram'
        return render(request,"statistics/plots.html",{'img_list':img_list,
                                                         'plates':plates,
                                                         'form':form,
                                                         'url_name':url_name,
                                                         'field_list':field_list,
                                                         })


#=============================================================================
## stable views for compound analysis
class dendrogram(view_stat_class):
    def c(self,request):
        
        img_list = []    
        data=self.data

        distance,method,distance_y,method_y = self._dendro_para(request)

        entry_list=data.objects.filter(ishit=1)
        #entry_list = compound.objects.filter(plate = '3267')#.filter(well = 'A05')
        fp2_list = []
        plate_well_list = []
        for e in entry_list:
            if e.compound_pointer:
                fp2_list.append(e.compound_pointer.fp2)
                plate_well_list.append(str(e.plate)+'_'+e.well)  
        
        if len(fp2_list)>1 and len(fp2_list)<100:
            c = clust.plot_dendro(fp2_list,plate_well_list,distance = distance,method = method )
            img_list.append(c)
            
        #    return HttpResponse(c)
            
        else:
            messages.warning(request,'Hit list compound numbers has to be within (1,100).')

        url_name = 'stat_dendrogram'
        return render(request,"statistics/clust.html",{'img_list':img_list,
                                                             'url_name':url_name,
                                                             })


class dendrogram2d(view_stat_class):
    #has bug
    def c(self,request):
        cmap_list = self._cmap_list()    
        
        if request.POST.get('heatmap_color'):
            cmap=request.POST.get('heatmap_color')
        else:
            cmap = 'YlGnBu'
            
        distance,method,distance_y,method_y = self._dendro_para(request)
    #    raise Exception(_dendro_para(request))


        img_list = []    
        
        entry_list = compound.objects.filter(plate = '3267')#.filter(well = 'A05')
        fp2_list = []
        plate_well_list = []
        for e in entry_list[:50]:
            fp2_list.append(e.fp2)
            plate_well_list.append(str(e.plate)+'_'+e.well)  
        
        c = clust.plot_dendro2d(fp2_list,plate_well_list,cmap=cmap, distance = distance, method = method,distance_y = distance_y, method_y = method_y  )
        img_list.append(c)
        
    #    return HttpResponse(c)
        url_name = 'stat_2ddendrogram'
        return render(request,"statistics/clust.html",{'img_list':img_list,
                                                         'url_name':url_name,
                                                         'cmap_list':cmap_list
                                                         })



#=============================================================================
## Testing views

class fingerprint_cluster(view_stat_class):
    def c(self,request):

        entry_list = compound.objects.filter(plate = '3266')#.filter(well = 'A05')
        fp2_list = []
        for entry in entry_list[:6]:
            fp2_list.append(entry.fp2)
        
    #    c = cluster.test_hierarchical_cluster(fp2_list)
        c = clust.test_tanimoto(fp2_list)
        
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
     
