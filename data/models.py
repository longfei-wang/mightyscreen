from django.db import models
from main.models import project
from mongoengine import *
import datetime
import collections
# Create your models here.

#automatically generate data model(table) for each project with their specific readouts
#figured that the table would be too big to store all the data. 
#A HTS project can easily have millions of entries. Better handle project seperately

field=collections.namedtuple('field',['name','verbose_name','path'])

class project_data_base(Document):

    meta={'abstract':True}
    
    hidden_fields=['id','create_by','platewell','submission','readout','score']#obsolete
    visible_fields=['plate','well','create_date','welltype','hit']
    
    def __init__(self,*args,**kwargs):
 
        super(project_data_base,self).__init__(*args,**kwargs)
        
        if self.pk:#if this is a instance, map all readout and scores to attributes and create field_list mapper
            
                        
            for j in self.readouts:
                n=0
                for i in self.reps:
                    try:#if not exist then None
                        setattr(self,j+'_'+i,self.readout[j][n])
                    except:
                        setattr(self,j+'_'+i,None)
                    n+=1

            for k in self.scores:
                try:
                    setattr(self,k,self.score[k])
                except:
                    setattr(self,k,None)

    @classmethod
    def field_list(self):        
        """field list is a list of fieldname displayed name and it's real path for query"""

        x = [field(i,self._fields[i].verbose_name if self._fields[i].verbose_name else i,i) for i in self.visible_fields]#get all field we can display
        
        for j in self.readouts:
            n=0
            for i in self.reps:
                x.append(field(j+'_'+i,j+'_'+i,'readout__'+j+'__'+str(n)))
                n+=1

        for k in self.scores:
            x.append(field(k,k,'score__'+k))
        return x

    @classmethod
    def set_proj(self,proj):
        self.readouts=proj.readouts()
        self.scores=proj.scores()
        self.reps=proj.rep()



    plate=StringField(max_length=20)
    well=StringField(max_length=20)
    platewell=StringField(max_length=50,required=True)  
    library=StringField(max_length=50,required=True)#library name should be unique
    #compound=ReferenceField(lib)
    
    hit=IntField(default=0)

    wtchoice = (
    ('E','empty'),
    ('P','positive control'),
    ('N','negative control'),
    ('B','bad well'),
    ('X','compound'),
    )
    welltype=StringField(max_length=1,choices=wtchoice,default='X')

    submission=IntField()
    create_date = DateTimeField(default=datetime.datetime.now)
    create_by = IntField()

    readout=DictField()
    score=DictField()

