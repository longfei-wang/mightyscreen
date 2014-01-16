from mongoengine import *
import collections
# Create your models here.


field=collections.namedtuple('field',['name','verbose_name','path'])

class library(Document):
    
    def __unicode__(self):
        return self.library_name

    library_name = StringField(max_length = 30)
    description=StringField(max_length=200)
    
    meta = {
    'indexes': [
        {'fields': ['library_name'], 'unique': True,
          'sparse': False, 'types': False },
    ],
    }


class compound(Document):
    
    visible_fields='sub_library_name pubchem_cid chemical_name molecular_weight formula tpsa logp canonical_smiles svg'.split()

    hidden_fields=['plate_well','sdf','id','fp2','fp3','fp4','plate','well']


    def __unicode__(self):
        return (self.plate_well)

    @classmethod
    def field_list(self):        
        """field list is a list of fieldname displayed name and it's real path for query
        This is only for datalist"""

        x = [field(i,self._fields[i].verbose_name if self._fields[i].verbose_name else i,'compound__'+i) for i in self.visible_fields]#get all field we can display
        return x

    library_name = StringField(max_length = 30)
    sub_library_name = StringField(max_length=50)
    facility_reagent_id = StringField(max_length = 30)
    plate = StringField(max_length=20)
    well = StringField(max_length = 20)
    plate_well = StringField(max_length = 20)
    pubchem_cid = StringField(max_length = 20)
    chemical_name = StringField()
    molecular_weight = DecimalField()
    formula = StringField(max_length = 30)
    tpsa = DecimalField()
    logp = DecimalField()
    inchikey = StringField(max_length = 30)
    canonical_smiles = StringField()
    inchi = StringField()
    fp2 = StringField()
    fp3 = StringField(max_length = 50)
    fp4 = StringField()
    svg = StringField(verbose_name='Structure')
    sdf = StringField()


    meta = {
    'indexes': [
        {'fields': ['plate_well'], 'unique': True,
          'sparse': True, 'types': False },
    ],
    }    
