# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'data.datetime'
        db.delete_column(u'main_data', 'datetime')

        # Adding field 'data.create_date'
        db.add_column(u'main_data', 'create_date',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'data.datetime'
        db.add_column(u'main_data', 'datetime',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 12, 9, 0, 0)),
                      keep_default=False)

        # Deleting field 'data.create_date'
        db.delete_column(u'main_data', 'create_date')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'main.additional_compound_info': {
            'Meta': {'object_name': 'additional_compound_info'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'main.compound': {
            'Meta': {'object_name': 'compound'},
            'additional_properties': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.additional_compound_info']"}),
            'canonical_smiles': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'chemical_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'facility_reagent_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'formula': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'fp2': ('django.db.models.fields.TextField', [], {}),
            'fp3': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'fp4': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inchi': ('django.db.models.fields.TextField', [], {}),
            'inchikey': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'library_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'logp': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '4'}),
            'molecular_weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '5'}),
            'plate': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'plate_well': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'pubchem_cid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sdf': ('django.db.models.fields.TextField', [], {}),
            'sub_library_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'svg': ('django.db.models.fields.TextField', [], {}),
            'tpsa': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'main.data': {
            'Meta': {'object_name': 'data'},
            'create_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'replicate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'main.data_readout': {
            'Meta': {'object_name': 'data_readout'},
            'data_entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.data']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reading': ('django.db.models.fields.TextField', [], {}),
            'readout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.readout']"})
        },
        u'main.experiment': {
            'Meta': {'object_name': 'experiment'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'readout': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['main.readout']", 'symmetrical': 'False'})
        },
        u'main.fileformat': {
            'Meta': {'object_name': 'fileformat'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'main.library': {
            'Meta': {'object_name': 'library'},
            'compounds': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.compound']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'sub_librarys': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.sub_library']"})
        },
        u'main.plate': {
            'Meta': {'object_name': 'plate'},
            'columns': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'numofwells': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'rows': ('django.db.models.fields.TextField', [], {})
        },
        u'main.project': {
            'ID': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'Meta': {'object_name': 'project'},
            'agreement': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.experiment']"}),
            'fileformat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.fileformat']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'plate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.plate']"}),
            'replicate': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        },
        u'main.rawdatafile': {
            'Meta': {'object_name': 'rawDataFile'},
            'datafile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'main.readout': {
            'Meta': {'object_name': 'readout'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'main.sub_library': {
            'Meta': {'object_name': 'sub_library'},
            'compounds': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.compound']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sub_library_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'super_library': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'main.submission': {
            'Meta': {'object_name': 'submission'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submit_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'submit_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'main.submission_plate_list': {
            'Meta': {'object_name': 'submission_plate_list'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'messages': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submission_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"})
        }
    }

    complete_apps = ['main']