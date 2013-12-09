from django.db import models

# Create your models here.

#==============================================================================
## test models from QY

#class for uploaded files
class rawDataFile(models.Model):
    def __unicode__(self):
        return self.readout
    
    datafile = models.FileField(upload_to = 'rawdata_test_%Y%m%d')
    

class compound(models.Model):
    def __unicode__(self):
        return (self.library_name + ' '+ self.plate_well)      
    library_name = models.ForeignKey('library')
    sub_library_name = models.ForeignKey('sub_library')
    facility_reagent_id = models.CharField(max_length = 30)
    plate = models.IntegerField(default=0)
    well = models.CharField(max_length = 20)
    plate_well = models.CharField(max_length = 20)
    pubchem_cid = models.IntegerField(default=0)
    chemical_name = models.CharField(max_length = 30)
    molecular_weight = models.DecimalField(max_digits=10, decimal_places=5)
    formula = models.CharField(max_length = 30)
    tpsa = models.DecimalField(max_digits=8, decimal_places=2)
    logp = models.DecimalField(max_digits=8, decimal_places=4)
    inchikey = models.CharField(max_length = 30)
    canonical_smiles = models.CharField(max_length = 100)
    inchi = models.TextField()
    fp2 = models.TextField()
    fp3 = models.CharField(max_length = 50)
    fp4 = models.TextField()
    svg = models.TextField()
    sdf = models.TextField()
#    additional_properties = models.ForeignKey('additional_compound_info')

class additional_compound_info(models.Model):
    pass

class library(models.Model):
    def __unicode__(self):
        return self.library_name
    library_name = models.CharField(max_length = 30)
    sub_librarys = models.CharField(max_length = 30)
    compounds = models.CharField(max_length = 30)    
    
class sub_library(models.Model):
    def __unicode__(self):
        return self.sub_library_name 
    sub_library_name = models.CharField(max_length = 30)
    super_library = models.ForeignKey('library') 
    compounds = models.CharField(max_length = 30)
