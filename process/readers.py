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
from jobtastic import JobtasticTask
from library.models import *
import sys

fs = GridFSStorage()

class reader():#a base class for all file format
    
    table_reg=dict()
    param=dict()
    map=defaultdict(lambda: defaultdict(dict))

    def __init__(self,**kwargs):
        
        if 'param' in kwargs:# this is for celery passing params to restore object

            self.param=kwargs['param']

        if 'datafile' in kwargs:
            
            datafile=kwargs['datafile']

            #save the file to gridfs temporarily
            self.param['filename'] = fs.save(datafile.name,datafile)  
    
        
        if 'proj_id' in kwargs:
            
            self.param['proj_id']=kwargs['proj_id']
            

        if 'form' in kwargs:
            #get the form 
            form = kwargs['form']

            self.param['proj_id']=form.get('proj_id')
            self.param['filename'] = form.get('filename')
            self.param['user_id']=form.get('user_id')
            self.param['library']=form.get('library')
            self.param['table_count']=form.get('table_count')
            self.param['primary_key']=form.get('primary_key')
            #what plates to update
            plates_num=0
            plates=[]
            
            if form.get('plate_num'):
                for i in range(1,int(form.get('plate_num'))+1):
                    if form.get('plate_'+str(i)):
                        plates.append(form.get('plate_'+str(i)))
                        plates_num+=1

                self.param['plates_num']=plates_num
                self.param['plates']=plates

        self.read_param()


    def read_param(self):
        
        self.proj_id=self.param['proj_id']
        self.p=project.objects.get(pk=self.proj_id)


        self.readout=self.p.readout
        self.readout_num=self.readout.count()

        try:#list file no need for these
            self.replicate=self.p.rep()
            self.replicate_num=len(self.replicate)
            self.row=self.p.plate.row()
            self.col=self.p.plate.col()
            self.wells=self.p.plate.numofwells
        except:
            pass

        self.datetime=dt.datetime.now()

        self.read_file()

        if 'user_id'in self.param:
            self.user = User.objects.get(id=self.param['user_id'])

        if 'plates_num' in self.param:
            self.plates_num=self.param['plates_num']

        if 'plates' in self.param:
            self.plates=self.param['plates']

    def get_data(self):
        
        from data.models import project_data_base
        exec('class proj_data_%s(project_data_base):pass;'%str(self.proj_id))
        exec('data = proj_data_%s'%str(self.proj_id))
        data.set_proj(project.objects.get(pk=self.proj_id))
        
        return data


    def read_file(self):
        
	filename=self.param['filename']
        filetype=filename.split(".")[-1]
        datafile = fs.open(filename)
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















    def parse(self,*args,**kwargs):
        """Determine the data type (list or grid) 
        scan the datafile
        generate forms based on that"""

        if self.is_list():
            return self.parse_list(*args,**kwargs)
        else:
            return self.parse_grid(*args,**kwargs)


    def parse_list(self):
        """process a list file"""

        self.col_names=list()

        for col in self.rawdata[0]:
            self.col_names.append(col)

        return self



    def parse_grid(self):
        """# process the data define where table are, also check if file is legit"""
        

        n=0
        self.table_count=0
        for row in self.rawdata:#read through whole file and find out all the tables
            n+=1
            for m in self.readout.all():
                if m.identifier in row[0]:
                    result=self.is_table(n)
                    if result:
                        if result['x']>=len(self.col) and result['y']>=len(self.row):
                            self.table_reg[result['start']]=m.name
                            self.table_count+=1


        return self


















    
    def render(self,*args,**wargs):

        if self.is_list():
            return self.render_list(*args,**wargs)
        else:
            return self.render_grid(*args,**wargs)


    def render_grid(self,request):
        if self.wells==1536:
	    #raise Exception(self.table_count)
            self.plates_num =  self.table_count * 4 / (self.replicate_num * self.readout_num)
        else:
            self.plates_num =  self.table_count / (self.replicate_num * self.readout_num)

        #return a html form that ask for all the information we need
        response = get_template('process/griduploadform.html').render(
                    RequestContext(request,{
                    'library':library.objects.all(),
                    'platerange': range(1,self.plates_num+1),
                    'filename':self.param['filename'],
                    'proj_id':self.p.id,
                    'plate_num':self.plates_num,
                    'table_count':self.table_count,
                    })
                    )

        return response
    
    def render_list(self,request):
        response = get_template('process/listuploadform.html').render(
                    RequestContext(request,{
                    'library':library.objects.all(),
                    'filename':self.param['filename'],
                    'proj_id':self.p.id,
                    'cols':self.col_names,
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
                raise Exception('not enough talbes')#raise exception might be good
            
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
















    
    def save(self,*args,**wargs):

        if self.is_list():
            return self.save_list(*args,**wargs)
        else:
            return self.save_grid(*args,**wargs)

    def save_grid(self,job):
        """#save tables into database row by row, might take some time."""

        self.map_table()

        data=self.get_data()

        results=[]

        for pla in range(self.plates_num):            

            for row in range(len(self.row)):

                for col in range(len(self.col)):

                    platewell=self.plates[pla]+self.row[row]+self.col[col]
                    
                    try:#check if this well has coresponding compound in our library
                        cmpd=compound.objects.get(plate_well = platewell,library_name=self.param['library'])
                    except:
                        cmpd=None
                    

                    #update_or_create: if same well already exists, it will be over written.
                    entry, created=data.objects.get_or_create(
                    library = self.param['library'],
                    platewell=platewell,
                    )

                    entry.plate = self.plates[pla]
                    entry.well=self.row[row]+self.col[col]
                    entry.create_date=self.datetime
                    entry.create_by=self.user.pk
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
                            
            
            job.update_progress((range(self.plates_num).index(pla)+1),self.plates_num)
            
            results.append(self.plates[pla])

        fs.delete(self.param['filename'])#if save is successfull delete the file in fs
        
        return results

    def save_list(self,job):

        data=self.get_data()
        num_rows=len(self.rawdata)
        cur_row=0

        for row in self.rawdata[1:]:
            
            cur_row+=1

            platewell = row[self.col_names.index(self.param['primary_key'])]

            try:#check if this well has coresponding compound in our library
                cmpd=compound.objects.get(plate_well = platewell,library_name=self.param['library'])
            except:
                cmpd=None

            entry, created = data.objects.get_or_create(
                library=self.param['library'],
                platewell=platewell,
                )

            entry.create_date=self.datetime
            entry.create_by=self.user.pk
            entry.compound=cmpd
        
            readout=[]

            for i in self.readout.all():
                if i.name in self.col_names:
                    #print >>sys.stderr, i.name,self.col_names 
                    entry.readout[i.name]=[row[self.col_names.index(i.name)]]

            entry.save()

            job.update_progress(cur_row,num_rows)

        fs.delete(self.param['filename'])#if save is successfull delete the file in fs

        return num_rows-1