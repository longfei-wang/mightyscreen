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

    hidden_fields=['plate_well','sdf','id','fp2','fp3','fp4','plate','well']

    library_name = models.ForeignKey('library')
    sub_library_name = models.CharField(max_length=100)
    facility_reagent_id = models.CharField(max_length = 100)
    plate = models.IntegerField()
    well = models.CharField(max_length = 20)
    plate_well = models.CharField(max_length = 20,unique=True)
    pubchem_cid = models.IntegerField(null=True)
    chemical_name = models.TextField()
    molecular_weight = models.DecimalField(max_digits=10, decimal_places=5)
    formula = models.CharField(max_length = 100)
    tpsa = models.DecimalField(max_digits=8, decimal_places=2)
    logp = models.DecimalField(max_digits=8, decimal_places=4)
    inchikey = models.CharField(max_length = 100)
    canonical_smiles = models.TextField()
    inchi = models.TextField()
    fp2 = models.TextField()
    fp3 = models.CharField(max_length = 50)
    fp4 = models.TextField()
    svg = models.TextField(verbose_name='Structure')
    sdf = models.TextField()


class library(models.Model):
    def __unicode__(self):
        return self.library_name
    library_name = models.CharField(unique=True,max_length = 100)
    number_of_compounds = models.IntegerField(default=0)

#Serializer for REST framework

from rest_framework import serializers

class compound_serializer (serializers.ModelSerializer):
    library_name = serializers.StringRelatedField()
    sub_library_name = serializers.StringRelatedField()

    class Meta:
        model = compound
        fields = 'library_name sub_library_name facility_reagent_id plate well plate_well pubchem_cid chemical_name molecular_weight formula tpsa logp inchikey canonical_smiles inchi svg'.split()
        
