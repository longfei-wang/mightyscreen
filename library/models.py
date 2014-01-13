from mongoengine import *

# Create your models here.

#==============================================================================
## test models from QY

#class for uploaded files
#class rawDataFile(models.Model):
#    def __unicode__(self):
#        return self.readout
#    
#    datafile = models.FileField(upload_to = 'rawdata_test_%Y%m%d')


class library(Document):
    
    def __unicode__(self):
        return self.library_name

    name = StringField(max_length = 30)
    description=StringField(max_length=200)


class compound(Document):
    
    def __unicode__(self):
        return (self.plate_well)

    hidden_fields=['plate_well','sdf','id','fp2','fp3','fp4','plate','well']

    library_name = ReferenceField(library)
    sub_library_name = StringField(max_length=50)
    facility_reagent_id = StringField(max_length = 30)
    plate = StringField(max_length=20)
    well = StringField(max_length = 20)
    plate_well = StringField(max_length = 20)
    pubchem_cid = IntField()
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


    
