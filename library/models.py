from django.db import models

# Create your models here.

#==============================================================================
## test models from QY

#class for uploaded files
#class rawDataFile(models.Model):
#    def __unicode__(self):
#        return self.readout
#    
#    datafile = models.FileField(upload_to = 'rawdata_test_%Y%m%d')
    

class compound(models.Model):
    def __unicode__(self):
        return (self.plate_well)      
    library_name = models.ForeignKey('library')
    sub_library_name = models.ForeignKey('sub_library')
    facility_reagent_id = models.CharField(max_length = 30)
    plate = models.IntegerField(default=0)
    well = models.CharField(max_length = 20)
    plate_well = models.CharField(max_length = 20)
    pubchem_cid = models.IntegerField(default=0)
    chemical_name = models.TextField()
    molecular_weight = models.DecimalField(max_digits=10, decimal_places=5)
    formula = models.CharField(max_length = 30)
    tpsa = models.DecimalField(max_digits=8, decimal_places=2)
    logp = models.DecimalField(max_digits=8, decimal_places=4)
    inchikey = models.CharField(max_length = 30)
    canonical_smiles = models.TextField()
    inchi = models.TextField()
    fp2 = models.TextField()
    fp3 = models.CharField(max_length = 50)
    fp4 = models.TextField()
    svg = models.TextField()
    sdf = models.TextField()


    
class sub_library(models.Model):
    def __unicode__(self):
        return self.sub_library_name 
    sub_library_name = models.CharField(max_length = 30)
    super_library = models.ForeignKey('library')
    number_of_compounds = models.IntegerField(default=0)

class library(models.Model):
    def __unicode__(self):
        return self.library_name
    library_name = models.CharField(max_length = 30)
    number_of_sub_librarys = models.IntegerField(default=0)
    number_of_compounds = models.IntegerField(default=0)