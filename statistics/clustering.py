#!/usr/bin/env python
# -*- coding: utf-8 -*-

# To used as a stand alone scripts called by statistics views 
import scipy
import pylab, scipy.optimize,numpy, scipy.stats

#from scipy import *
import cStringIO
import StringIO
import math
import random
import copy


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
    Default output format is PNG. \n
    SVG format doesn't work yet. This function will be updated for svg output in the future    
    """
    if format_out=='png':
        sio = cStringIO.StringIO()
        pylab.savefig(sio, format='png')
        image_string = """<img src="data:image/png;base64,%s"/><br>""" % sio.getvalue().encode("base64").strip()
    elif format_out=='svg':
        sio = StringIO.StringIO()
        pylab.savefig(sio,format ='svg')
        sio.seek(0)
        image_string = (sio.buf + '<br>' )   
    return image_string

# Four essential functions to handle finger print 
def _fp_to_ascii( fp):
    return "".join( ["%08x"%num for num in fp])
    
def _ascii_to_fp( ascii):
    ret = []
    for i in range( 0, 256, 8):
        ret.append( int( ascii[i:i+8], 16))
    return ret

def _count_bits( num):
    count = 0
    while num:
        count += num & 1
        num >>= 1
    return count

def _tanimoto(fp1,fp2):
    """input two finger prints in fp format\n
    return tanimoto coefficient between the two fps\n
        
    fingerprint stored in library are in ascii format, need to use \n
    ascii_to_fp(fp) function to convert it back first    
    """
    common,all =0,0
    for i, num in enumerate(fp2):
        num1 = fp1[i]
        common += _count_bits(num1 & num)
        all += _count_bits(num1 | num)
    tanimoto = 1.0*common/all
    return tanimoto



##==============================================================================
## test views


def _fp2_to_distancematrix(fp2_list):
    n = len(fp2_list)
    matrix = scipy.zeros([n,n])
    for i in range(n):
        for j in range(n):
            fp1 = _ascii_to_fp(fp2_list[i])
            fp2 = _ascii_to_fp(fp2_list[j])
            similarity = _tanimoto(fp1,fp2)
            distance = 1 - similarity
            matrix[i,j]=distance
    return matrix
        


def test_cluster(data_in, n = 10):
    """use k_means_clustering"""    
    
    from numpy import vstack,array
    from numpy.random import rand
    from scipy.cluster.vq import kmeans,vq
    
    fig = pylab.figure(figsize=(12,6))    
    
    # data generation
#    data = vstack((rand(150,2) + array([.5,.5]),rand(150,2)))
    data = vstack((data_in))
    ## computing K-Means with K = 2 (2 clusters)
    #centroids,_ = kmeans(data,10)
    ## assign each sample to a cluster
    #idx,_ = vq(data,centroids)
    #
    ## some plotting using numpy's logical indexing
    #plot(data[idx==0,0],data[idx==0,1],'ob',
    #     data[idx==1,0],data[idx==1,1],'or')
    #plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
    #show()
    
    # now with K = 3 (3 clusters)

    centroids,_ = kmeans(data,n)
    idx,_ = vq(data,centroids)
    
    color_s = 'rcgmbyk'
    for i in range(n):
        pylab.plot(data[idx==i],data[idx==i],'o', color = color_s[i%7])

#    pylab.plot(centroids[:,0],centroids[:,1],'sm',markersize=8)

    image_string = _fig_out()
    return image_string

def test_hierarchical_cluster(fp2_list):
    """ modified from
    http://stackoverflow.com/questions/2982929
        
    works for now!
    """    
    
    import scipy
    import pylab
    import scipy.cluster.hierarchy as sch
    import fastcluster as fch
    
    D = _fp2_to_distancematrix(fp2_list)
    fig = pylab.figure(figsize=(8,8))
    ax1 = fig.add_axes([0.09,0.1,0.2,0.6])
    Y = fch.linkage(D, method='centroid')
    Z1 = sch.dendrogram(Y, orientation='right')
    ax1.set_xticks([])
    ax1.set_yticks([])
    
    # Compute and plot second dendrogram.
    ax2 = fig.add_axes([0.3,0.71,0.6,0.2])
    Y = fch.linkage(D, method='single')
    Z2 = sch.dendrogram(Y)
    ax2.set_xticks([])
    ax2.set_yticks([])
    
    # Plot distance matrix.
    axmatrix = fig.add_axes([0.3,0.1,0.6,0.6])
    idx1 = Z2['leaves']
    idx2 = Z2['leaves']
    D = D[idx1,:]
    D = D[:,idx2]
    im = axmatrix.matshow(D, aspect='auto', origin='lower', cmap=pylab.cm.YlGnBu)
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])
    
    # Plot colorbar.
    axcolor = fig.add_axes([0.91,0.1,0.02,0.6])
    pylab.colorbar(im, cax=axcolor)
#    pylab.savefig('test_clustering.html', format = 'svg')
    image_string = _fig_out()
    
    return image_string
    
    
def test_networkx(fp2_list):   
    """doesn't work yet"""
    import networkx as nx
    D = _fp2_to_distancematrix(fp2_list)
    pylab.figure()    
    G = nx.DiGraph()
    labels = {}
    for n in range(len(D)):
        for m in range(len(D)-(n+1)):
            G.add_edge(n,n+m+1, weight = D[n][n+m+1], length =D[n][n+m+1] )
            labels[ (n,n+m+1) ] = str(round(D[n][n+m+1],2))
            
    pos=nx.random_layout(G)
    
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels,font_size=8)

    nx.draw(G, pos)
    image_string = _fig_out()
    
    return image_string   


def test_bin(fp2_list):   
    """  """
    import scipy
    import pylab
    import scipy.cluster.hierarchy as sch
    import fastcluster as fch
    
    D = _fp2_to_distancematrix(fp2_list)
    L = sch.linkage(D, method='single')
    ind = sch.fcluster(L, 1.1, criterion="distance")
    bins = len(set(ind))
    
    return bins