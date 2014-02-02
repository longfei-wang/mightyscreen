#!/usr/bin/env python
# -*- coding: utf-8 -*-

# To used as a stand alone scripts called by statistics views 

import matplotlib
matplotlib.use('Agg')

import pylab, scipy.optimize,numpy, scipy.stats
import itertools

#from scipy import *
import StringIO

#=============================================================================
## facilitate functions    
    
def _split_position(position_list):
    xs_column=[]
    ys_row=[]
    for line in position_list:
        xs_column.append(int(line[1:]))
        y_letter = line[0]
        y_number = _translate(str(y_letter))
        ys_row.append(y_number)
    return [xs_column,ys_row]

def _translate(str_or_int):
    s='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    d1 = {}
    d2 = {}
    for n in range(len(s)):
        d1.update({s[n]:(n+1)})
        d2.update({(n+1):s[n]})
        
    if type(str_or_int)== str and str_or_int in d1.keys():
        return d1[str_or_int]
    elif type(str_or_int)==int and str_or_int in d2.keys():
        return d2[str_or_int]

def _findNearest(array,value):
    return abs(scipy.asarray(array)-value).argmin()

def _func_sigmoid(x,EC50,k,base,amp):
    return amp / (1 + 10**(-1*(x-EC50))) + base

def _gauss(x, a, b, c):
    return a * pylab.exp(-(x - b)**2.0 / (2 * c**2))

def _figsize(x = 8, y = 5):
    """ To set the output figure size \n
    Default is 6 x 3"""
    figsize=(x,y)
    return figsize

def _plate_base(plate_type):
    s_384 = """A01 A02 A03 A04 A05 A06 A07 A08 A09 A10 A11 A12 A13 A14 A15 A16 A17 A18 A19 A20 A21 A22 A23 A24 
    B01 B02 B03 B04 B05 B06 B07 B08 B09 B10 B11 B12 B13 B14 B15 B16 B17 B18 B19 B20 B21 B22 B23 B24 
    C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11 C12 C13 C14 C15 C16 C17 C18 C19 C20 C21 C22 C23 C24 
    D01 D02 D03 D04 D05 D06 D07 D08 D09 D10 D11 D12 D13 D14 D15 D16 D17 D18 D19 D20 D21 D22 D23 D24 
    E01 E02 E03 E04 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E16 E17 E18 E19 E20 E21 E22 E23 E24 
    F01 F02 F03 F04 F05 F06 F07 F08 F09 F10 F11 F12 F13 F14 F15 F16 F17 F18 F19 F20 F21 F22 F23 F24 
    G01 G02 G03 G04 G05 G06 G07 G08 G09 G10 G11 G12 G13 G14 G15 G16 G17 G18 G19 G20 G21 G22 G23 G24 
    H01 H02 H03 H04 H05 H06 H07 H08 H09 H10 H11 H12 H13 H14 H15 H16 H17 H18 H19 H20 H21 H22 H23 H24 
    I01 I02 I03 I04 I05 I06 I07 I08 I09 I10 I11 I12 I13 I14 I15 I16 I17 I18 I19 I20 I21 I22 I23 I24 
    J01 J02 J03 J04 J05 J06 J07 J08 J09 J10 J11 J12 J13 J14 J15 J16 J17 J18 J19 J20 J21 J22 J23 J24 
    K01 K02 K03 K04 K05 K06 K07 K08 K09 K10 K11 K12 K13 K14 K15 K16 K17 K18 K19 K20 K21 K22 K23 K24 
    L01 L02 L03 L04 L05 L06 L07 L08 L09 L10 L11 L12 L13 L14 L15 L16 L17 L18 L19 L20 L21 L22 L23 L24 
    M01 M02 M03 M04 M05 M06 M07 M08 M09 M10 M11 M12 M13 M14 M15 M16 M17 M18 M19 M20 M21 M22 M23 M24
    N01 N02 N03 N04 N05 N06 N07 N08 N09 N10 N11 N12 N13 N14 N15 N16 N17 N18 N19 N20 N21 N22 N23 N24
    O01 O02 O03 O04 O05 O06 O07 O08 O09 O10 O11 O12 O13 O14 O15 O16 O17 O18 O19 O20 O21 O22 O23 O24
    P01 P02 P03 P04 P05 P06 P07 P08 P09 P10 P11 P12 P13 P14 P15 P16 P17 P18 P19 P20 P21 P22 P23 P24"""
    if plate_type == '384':    
        well_list = s_384.split()
    return well_list

def _fig_out(format_out ='svg'):
    """ Write the output figure generated by pylab into a string that can be used in html\n
    Default output format is svg now. \n
    Inspired by codes from following pages: \n
    http://stackoverflow.com/questions/5453375  \n    
    """
    if format_out=='png':
        import cStringIO
        sio = cStringIO.StringIO()
        pylab.savefig(sio, format='png')
        image_string = """<img src="data:image/png;base64,%s"/><br>""" % sio.getvalue().encode("base64").strip()
    elif format_out=='svg':
        sio = StringIO.StringIO()
        pylab.savefig(sio,format ='svg')
        sio.seek(0)
        image_string = (sio.buf + '<br>' )   
    return image_string


def _dot_color_dict():
    color_dict = {'B':['bad well', '#bdbdbd'], 
                  'P':['positive\ncontrol', '#de2d26'],
                  'N':['negative\ncontrol', '#0000CC'],
                  'E':['empty', '#ffeda0'],
                  'X':['compound', '#41b6c4'],
                    }
    return color_dict
    

##==============================================================================



#Define fit functions
def plot_sigmoid_binding(file_name,x_column_number = 1,y_column_number = 2):
    fitfunc = _func_sigmoid
    ## Initiate parameters
    xraw = _read_columns(file_name,x_column_number,y_column_number)[0]
    xs = numpy.log10(xraw)
    ys = _read_columns(file_name,x_column_number,y_column_number)[1]
#    ymin = min(ys)
#    ymax = max(ys)
#    y50 = (ymax - ymin) / 2 + ymin
#    idx = _findNearest(ys,y50)
#    EC50 = xs[idx]
#    k = 1
#    baseline = ymin
#    amplitude = ymax - ymin
    
    # fitting with fitfunc
    popt,pcov = scipy.optimize.curve_fit(fitfunc,xs,ys)
    
    ## debug code: """used to see the initial fit to confirm curve fitting make things better
    #print "guessing parameters ..."
    #guess = [EC50,k,baseline,amplitude]
    #print "guess: ", guess
    
    #print "fitting data ...\n""popt: ", popt
    
    ## Plot data
    x = scipy.linspace(min(xs),max(xs),100)
    
    pylab.figure()
    #plot raw data
    pylab.plot(xraw,ys,'ro', label='raw data')
    #pylab.plot(x,fitfunc(x,*guess), label='guess') # debug code
    #plot fitting curve    
    pylab.plot(10**x,fitfunc(x,*popt), 'b', label='Fitting curve\nEC50 = %e'%popt[0])
    pylab.xlabel("concentration")
    pylab.ylabel('Intenstiy')
    pylab.legend(loc='best')
    pylab.grid()
    #pylab.show()
    pylab.savefig('%s_binding.png'%file_name, dpi=300)
    
    pylab.figure()
    pylab.plot(xs,ys,'ro', label='raw data')
    #pylab.plot(x,fitfunc(x,*guess), label='guess') # debug code
    pylab.plot(x,fitfunc(x,*popt), 'b', label='Fitting curve\nEC50 = %e'%popt[0])
    pylab.xlabel("log[concentration]")
    pylab.ylabel('Intenstiy')
    pylab.legend(loc='best')
    pylab.grid()
    #pylab.show()
    pylab.savefig('%s_%s.png'%(file_name,fitfunc.__name__), dpi=300)



def plot_scatter(data_list,plate_well_list,well_type_list, plate_number = 1, sort = 'default'):
    xs = [n+1 for n in xrange(len(plate_well_list))]
    ys = data_list    
    if sort == 'default':    
        ys.sort()    
    
    
    color_dict =_dot_color_dict()
    
#    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xs,ys)    
#    z = numpy.polyfit(xs,ys,1)
#    fitfunc = numpy.poly1d(z)    

    ## Creat the canves    
    fig = pylab.figure(figsize=_figsize())   
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.7])
    plate_pro = "plate" if len(plate_number.split(','))==1 else "plates" 
    pylab.title('Scatter Plot\n %s: %s'%(plate_pro,plate_number))
    pylab.xlabel('Well Number')
    if sort =='sorted':
        pylab.xlabel('Arbitary Number')        
    pylab.ylabel('%s: %s'%(plate_pro,plate_number))
    pylab.xlim(min(xs)-10,max(xs)+10)       
    
#    x = scipy.linspace(min(xs),max(xs),100)
#    pylab.plot(x,fitfunc(x),'b', label=('fitting\n R=%f'%r_value))          
    
    # plot interactive layer    
    patch_id = []
    for n in range(len(xs)):
        patch_id.append(('patch_ax_%s'%plate_well_list[n]))
    well_types = []
    for x,y,w,gid in itertools.izip(xs,ys,well_type_list,patch_id):
        if w not in well_types:
            pylab.plot(x,y,'o', markersize=8, color = color_dict[w][1], gid = gid, label = color_dict[w][0].title())
            well_types.append(w)
        else:
            pylab.plot(x,y,'o', markersize=8, color = color_dict[w][1], gid = gid)  
    
    ## Plot legend
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5),prop={'size':12})

#    pylab.legend(loc='best') 
    image_string = _fig_out()
    return image_string



def plot_linearfit(data_a,data_b,plate_well_list, plate_number,well_type_list,label_x,label_y):
    
    xs = data_a
    ys = data_b
        

    color_dict =_dot_color_dict()
    
    
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xs,ys)    
    z = numpy.polyfit(xs,ys,1)
    fitfunc = numpy.poly1d(z)    

    ## Creat the canves    
    fig = pylab.figure(figsize=_figsize())   
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.7])
    plate_pro = "plate" if len(plate_number.split(','))==1 else "plates" 
    pylab.title('Data replicability\n %s: %s'%(plate_pro,plate_number))
    pylab.xlabel('%s of %s: %s'%(label_x,plate_pro, plate_number))
    pylab.ylabel('%s of %s: %s'%(label_y,plate_pro,plate_number))       
    
    x = scipy.linspace(min(xs),max(xs),100)
    pylab.plot(x,fitfunc(x),'b', label=('fitting\nR=%.3f'%r_value))          
    
    # plot interactive layer    
    patch_id = []
    for n in range(len(xs)):
        patch_id.append(('patch_ax_%s'%plate_well_list[n]))

    well_types = []
    for x,y,w,id in itertools.izip(xs,ys,well_type_list,patch_id):
        if w not in well_types:
            #pylab.scatter(x,y, s=60, c = color_dict[w][1], gid = id, label = color_dict[w][0].title())
            pylab.plot(x,y,'o', markersize=8, color = color_dict[w][1], gid = id, label = color_dict[w][0].title())
            well_types.append(w)
        else:
           # pylab.scatter(x,y, s=60, c = color_dict[w][1], gid = id)  
            pylab.plot(x,y,'o', markersize=8, color = color_dict[w][1], gid = id)  
    
    ## Plot legend
    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    
    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size':12})

#    pylab.legend(loc='best') 
    image_string = _fig_out()
    return image_string


def plot_histogram(data_list, plate_number = 1,bins = 100):
    """plot histogram, with gauss fitting \n
    Code modified from http://stackoverflow.com/questions/17779316
        
    If Guassin fit doesn't work then curve fit won't show anything.
    
    Need to improve to find a best fit function
    """
    ys = numpy.array(data_list)
#    ys = numpy.random.standard_normal(10000)
        
    fig = pylab.figure(figsize=_figsize())   
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.7])
    
    ## Plot the histogram    
    data = pylab.hist(ys, bins = bins,facecolor='green', alpha=0.5)

#    # Generate data from bins as a set of points 
#    x = [0.5 * (data[1][i] + data[1][i+1]) for i in xrange(len(data[1])-1)]
#    y = data[0]    
#    popt, pcov = scipy.optimize.curve_fit(_gauss, x, y)
#
#    # Plot the fitting data    
#    x_fit = pylab.linspace(x[0], x[-1], 100)
#    y_fit = _gauss(x_fit, *popt) 
#
#    pylab.plot(x_fit, y_fit, "r--",lw=1, label = "Gaussian Fit")
    
    ## legands and labels
    plate_pro = "plate" if len(plate_number.split(','))==1 else "plates" 
    pylab.title('Histogram\n %s: %s'%(plate_pro,plate_number))
    pylab.xlabel('%s: %s'%(plate_pro,plate_number))
    pylab.legend(loc='best') 
    pylab.xlim(min(ys)-10,max(ys)+10)    
    
    image_string = _fig_out()
    return image_string


def plot_heatmap(well, intensity,plate_well_list, plate_number = 1, cmap = 'jet_r', plate_type = '384'):
    """Plot heatmap of 384 plates by default \n
    Can be expanded to other plate form using _plate_base functio \n
    inspired by codes from following pages: \n
    http://stackoverflow.com/questions/5147112  \n
    """
    
    ## Read column and row to make the base of plate
    mock_well = _plate_base(plate_type)
    xsmock_column,ysmock_row = _split_position(mock_well)
    ysmock_row_inverse = numpy.multiply(ysmock_row,[-1]) 

    ## Read column and row from input to be plotted
    xs_column,ys_row = _split_position(well)
    ys_row_inverse = numpy.multiply(ys_row,[-1])

    ## Creat the canves    
    fig = pylab.figure(figsize=_figsize())   
    
    ## Plot colorbar
    ax2 = fig.add_axes([0.1, 0.1, 0.4, 0.03])
    norm = pylab.mpl.colors.Normalize(vmin=min(intensity), vmax=max(intensity))
    cb2 = pylab.mpl.colorbar.ColorbarBase(ax2, cmap=cmap,norm = norm,
                                          orientation='horizontal')       
    cb2.set_label("%s (color: %s)"%(plate_number.split()[-1], cmap))
    
    ## Plot the title section
    ax3 = fig.add_axes([0.05,0.93,0.85,0.02])
    ax3.spines['right'].set_color('none')
    ax3.spines['top'].set_color('none')
    ax3.spines['bottom'].set_color('none')
    ax3.spines['left'].set_color('none')
    pylab.xticks([]), pylab.yticks([])
    pylab.text(0.5,0.5, 'plate: %s'%(str(plate_number)),ha='center',va='bottom')

    
    ## Set plate axis, ticks, 
    ax1 = fig.add_axes([0.05, 0.20, 0.85, 0.73])    
    pylab.xlim(0,(max(xsmock_column)+1))
    pylab.ylim(((max(ysmock_row)+1))*-1,0)
    pylab.xticks([5, 10, 15,20])
    ytick_list = []
    ytick_showlist = []
    for n in ys_row_inverse:
        if n%2 == 1:
            ytick_list.append(n)
            ytick_showlist.append(_translate(int(n*-1)))
    pylab.yticks(ytick_list,ytick_showlist)          
    pylab.grid()
    
    
    ##plot empty plate
    if len(xs_column) !=384:
        pylab.scatter(xsmock_column,ysmock_row_inverse, s=100,c = 'w', cmap = cmap)
    
    ## plot data as heatmap
    pylab.scatter(xs_column,ys_row_inverse, s=100,c = intensity, cmap = cmap)
    
    ## plot interactive layer    
    patch_id = []
#    tooltip_id=[]
    for n in range(len(xs_column)):
        patch_id.append(('patch_ax_%s'%(plate_number.split()[-1]+'_'+plate_well_list[n])))
#        tooltip_id.append(('tooltip_ax_%d'%plate_well_list[n]))

    for x,y,id in itertools.izip(xs_column,ys_row_inverse,patch_id):    
       # pylab.scatter(x,y, s=100,alpha = 0.01, c= 'w', gid = id)
        pylab.plot(x,y,'o', markersize=10, color = 'w', gid = id, alpha=0.01)  
    
#    for tooltip, x, y, id  in itertools.izip(tooltips, xs_column, ys_row_inverse, tooltip_id):
#        ax1.annotate(
#            ('FP:'+str(tooltip)), 
#            xy = (x, y), xytext = (20, 20),
#            textcoords = 'offset points', ha = 'right', va = 'bottom',
#            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
#            gid=id,
#            )     
    
#    pylab.savefig('test_heatmap.html',format = 'svg')
    image_string = _fig_out()
    return image_string

