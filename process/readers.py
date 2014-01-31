from django.contrib.auth.models import User
from collections import defaultdict
from library.models import library, compound
import pandas as pd
import cPickle as pickle
import simplejson as json
import datetime as dt
from django.template import RequestContext
from django.template.loader import get_template
from django.core.context_processors import csrf
from main.models import project, submission
from mongoengine.django.storage import GridFSStorage
from library.models import *
from main.utils import job as jobclass

class reader(jobclass):#a base class for all file format
    
    table_reg=dict()   

    def __init__(self,**kwargs):
        
        if 'datafile' in kwargs:
            
            self.read_file(kwargs['datafile'])                   
        
        if 'proj_id' in kwargs:
            self.p=project.objects.get(pk=kwargs['proj_id'])
            self.readout=self.p.experiment.readout
            self.readout_num=self.readout.count()

        if 'form' in kwargs:
            form = kwargs['form']
            filename = form.get('filename')
            fs = GridFSStorage()
            self.read_file(fs.open(filename))
            self.proj_id=form.get('proj_id')
            self.user=User.objects.get(id=form.get('user_id'))
            self.p=project.objects.get(pk=self.proj_id)
            self.readout=self.p.experiment.readout
            self.readout_num=self.readout.count()
            self.replicate=self.p.rep()
            self.replicate_num=len(self.replicate)
            self.row=self.p.plate.row()
            self.col=self.p.plate.col()
            self.wells=self.p.plate.numofwells
            self.datetime=dt.datetime.now()
            self.map=defaultdict(lambda: defaultdict(dict))
            self.library=form.get('library')
            self.table_count=form.get('table_count')
            self.plates_num=0
            self.plates=[]
            for i in range(1,int(form.get('plate_num'))+1):
                if form.get('plate_'+str(i)):
                    self.plates.append(form.get('plate_'+str(i)))
                    self.plates_num+=1


    def parse(self,*args,**kwargs):
        """Determine the data type (list or grid) 
        scan the datafile
        generate forms based on that"""

        if self.is_list():
            return self.parse_list(*args,**kwargs)
        else:
            return self.parse_grid(*args,**kwargs)


    def read_file(self,datafile):
        
        filetype=datafile.name.split(".")[-1]

        if filetype=='csv':
            self.rawdata=pd.read_csv(datafile,header=None).fillna('').values
        else:
            raise Exception('Unsupported File Type!')
    

    def is_list(self):
        if '' not in self.rawdata[0]:
            return True

    def is_table(self,row):#tell if within +- 2 row current posistion is a table, if so return the dimension of this table
        start=0
        for i in range(row-2,row+3):
            if '' not in self.rawdata[i]:
                x=len(self.rawdata[i])
                start=i
                break
        n=start

        while '' not in self.rawdata[n]:
            n+=1
        y=n-row
        
        if y<1:
            return False

        return {'start':start,'x':x,'y':y}

    def test(self):

        return self.rawdata[10]


    def parse_list(self):
        return self



    def parse_grid(self):
        """# process the data define where table are, also check if file is legit"""
        
        self.row=self.p.plate.row()
        self.col=self.p.plate.col()
        self.replicate=self.p.rep()
        self.replicate_num=len(self.replicate)
        self.wells=self.p.plate.numofwells

        n=0
        self.table_count=0
        for row in self.rawdata:#read through whole file and find out all the tables
            n+=1
            for m in self.readout.all():
                if m.keywords in row[0]:
                    result=self.is_table(n)
                    if result:
                        if result['x']>=len(self.col) and result['y']>=len(self.row):
                            self.table_reg[result['start']]=m.name
                            self.table_count+=1




        return self

    def render(self,filename,request):

        if self.wells=='1536':
            self.plates_num =  self.table_count * 4 / (self.replicate_num * self.readout_num)
        else:
            self.plates_num =  self.table_count / (self.replicate_num * self.readout_num)

        #return a html form that ask for all the information we need
        response = get_template('process/griduploadform.html').render(
                    RequestContext(request,{
                    'library':library.objects.all(),
                    'platerange': range(1,self.plates_num+1),
                    'filename':filename,
                    'proj_id':self.p.id,
                    'plate_num':self.plates_num,
                    'table_count':self.table_count,
                    })
                    )

        return response
        
    def map_table(self):
        #creat pointers that point at each table

        replicate_count=0
        plate_count=0
        readout_list=list()

        if self.wells==384:
            
            if self.table_count < self.replicate_num*self.plates_num*self.readout_num:
                return False#raise exception might be good
            
            for i in sorted(self.table_reg):#go over each replicate and plate
                if self.table_reg[i] not in readout_list:
                    readout_list.append(self.table_reg[i]) 
                else:
                    readout_list=list()
                    readout_list.append(self.table_reg[i]) 
                    replicate_count+=1
                    if replicate_count==self.replicate_num:
                        replicate_count=0
                        plate_count+=1
                        if plate_count==self.plates_num:
                            break

                self.map[plate_count][replicate_count][self.table_reg[i]]=[i,1]
        
        elif self.wells==1536:

            if self.table_count*4 < self.replicate_num*self.plates_num*self.readout_num:
                return False#raise exception might be good

            for i in sorted(self.table_reg):#go over each replicate and plate
                if self.table_reg[i] not in readout_list:
                    readout_list.append(self.table_reg[i]) 
                else:
                    readout_list=list()
                    readout_list.append(self.table_reg[i]) 
                    replicate_count+=1
                    if replicate_count==self.replicate_num:
                        replicate_count=0
                        plate_count+=4
                        if plate_count>=self.plates_num:
                            break

                self.map[plate_count][replicate_count][self.table_reg[i]]=[i,1]
                self.map[plate_count+1][replicate_count][self.table_reg[i]]=[i,2]
                self.map[plate_count+2][replicate_count][self.table_reg[i]]=[i+1,1]
                self.map[plate_count+3][replicate_count][self.table_reg[i]]=[i+1,2]

        return self.map

    
    def save_grid(self,data):
        """#save tables into database row by row, might take some time."""
        
        self.map_table()

        if not self.sub:
            return
        


        for pla in range(self.plates_num):            

            for row in range(len(self.row)):

                for col in range(len(self.col)):

                    platewell=self.plates[pla]+self.row[row]+self.col[col]
                    
                    try:#check if this well has coresponding compound in our library
                        cmpd=compound.objects.get(plate_well = platewell,library_name=self.library)
                    except:
                        cmpd=None
                    

                    #update_or_create: if same well already exists, it will be over written.
                    entry, created=data.objects.get_or_create(
                    library = self.library,
                    platewell=platewell,
                    )

                    entry.plate = self.plates[pla]
                    entry.well=self.row[row]+self.col[col]
                    entry.submission=self.sub.pk
                    entry.create_date=self.datetime
                    entry.create_by=self.sub.submit_by.pk
                    entry.compound=cmpd

                    for i in self.readout.all():
                        readout=[] 
                        for rep in range(self.replicate_num):#all the readouts
                      
                            y=int(self.map[pla][rep][i.name][0])
                            x=int(self.map[pla][rep][i.name][1])

                            if self.wells==384:
                                readout.append(float(self.rawdata[row+y][col+x]))
                                #exec('entry.%(readout)s_%(rep)s=self.rawdata[row+y][col+x]'%{'readout':i,'rep':self.replicate[rep]})
                            elif self.wells==1536:
                                readout.append(float(self.rawdata[row*2+y][col*2+x]))
                                #exec('entry.%(readout)s_%(rep)s=self.rawdata[row*2+y][col*2+x]'%{'readout':i,'rep':self.replicate[rep]})
                        entry.readout[i.name]=readout
                    entry.save()
                            
            self.update((range(self.plates_num).index(pla)+1)/self.plates_num*100,';plate: %s uploaded'%self.plates[pla])

        self.complete()
        
        return self

