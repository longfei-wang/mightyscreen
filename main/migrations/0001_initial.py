# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'project'
        db.create_table(u'main_project', (
            ('ID', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('agreement', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('experiment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.experiment'])),
            ('plate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.plate'])),
            ('replicate', self.gf('django.db.models.fields.TextField')()),
            ('fileformat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.fileformat'])),
        ))
        db.send_create_signal(u'main', ['project'])

        # Adding M2M table for field user on 'project'
        m2m_table_name = db.shorten_name(u'main_project_user')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'main.project'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'user_id'])

        # Adding model 'experiment'
        db.create_table(u'main_experiment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'main', ['experiment'])

        # Adding M2M table for field readout on 'experiment'
        m2m_table_name = db.shorten_name(u'main_experiment_readout')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('experiment', models.ForeignKey(orm[u'main.experiment'], null=False)),
            ('readout', models.ForeignKey(orm[u'main.readout'], null=False))
        ))
        db.create_unique(m2m_table_name, ['experiment_id', 'readout_id'])

        # Adding model 'readout'
        db.create_table(u'main_readout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('keywords', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'main', ['readout'])

        # Adding model 'fileformat'
        db.create_table(u'main_fileformat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'main', ['fileformat'])

        # Adding model 'plate'
        db.create_table(u'main_plate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('numofwells', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('columns', self.gf('django.db.models.fields.TextField')()),
            ('rows', self.gf('django.db.models.fields.TextField')()),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal(u'main', ['plate'])

        # Adding model 'submission'
        db.create_table(u'main_submission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.project'])),
            ('submit_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('submit_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'main', ['submission'])

        # Adding model 'submission_plate_list'
        db.create_table(u'main_submission_plate_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('submission_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.submission'])),
            ('library', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('plate', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('messages', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'main', ['submission_plate_list'])

        # Adding model 'data'
        db.create_table(u'main_data', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('library', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('plate', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('well', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('replicate', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.project'])),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.submission'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('create_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('test', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'main', ['data'])

        # Adding model 'data_readout'
        db.create_table(u'main_data_readout', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data_entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.data'])),
            ('readout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.readout'])),
            ('reading', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'main', ['data_readout'])

        # Adding model 'rawDataFile'
        db.create_table(u'main_rawdatafile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datafile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'main', ['rawDataFile'])

        # Adding model 'compound'
        db.create_table(u'main_compound', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('library_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('sub_library_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('facility_reagent_id', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('plate', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('well', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('plate_well', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('pubchem_cid', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('chemical_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('molecular_weight', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=5)),
            ('formula', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('tpsa', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('logp', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=4)),
            ('inchikey', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('canonical_smiles', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('inchi', self.gf('django.db.models.fields.TextField')()),
            ('fp2', self.gf('django.db.models.fields.TextField')()),
            ('fp3', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('fp4', self.gf('django.db.models.fields.TextField')()),
            ('svg', self.gf('django.db.models.fields.TextField')()),
            ('sdf', self.gf('django.db.models.fields.TextField')()),
            ('additional_properties', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.additional_compound_info'])),
        ))
        db.send_create_signal(u'main', ['compound'])

        # Adding model 'additional_compound_info'
        db.create_table(u'main_additional_compound_info', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'main', ['additional_compound_info'])

        # Adding model 'library'
        db.create_table(u'main_library', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('library_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('sub_librarys', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.sub_library'])),
            ('compounds', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.compound'])),
        ))
        db.send_create_signal(u'main', ['library'])

        # Adding model 'sub_library'
        db.create_table(u'main_sub_library', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sub_library_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('super_library', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('compounds', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.compound'])),
        ))
        db.send_create_signal(u'main', ['sub_library'])


    def backwards(self, orm):
        # Deleting model 'project'
        db.delete_table(u'main_project')

        # Removing M2M table for field user on 'project'
        db.delete_table(db.shorten_name(u'main_project_user'))

        # Deleting model 'experiment'
        db.delete_table(u'main_experiment')

        # Removing M2M table for field readout on 'experiment'
        db.delete_table(db.shorten_name(u'main_experiment_readout'))

        # Deleting model 'readout'
        db.delete_table(u'main_readout')

        # Deleting model 'fileformat'
        db.delete_table(u'main_fileformat')

        # Deleting model 'plate'
        db.delete_table(u'main_plate')

        # Deleting model 'submission'
        db.delete_table(u'main_submission')

        # Deleting model 'submission_plate_list'
        db.delete_table(u'main_submission_plate_list')

        # Deleting model 'data'
        db.delete_table(u'main_data')

        # Deleting model 'data_readout'
        db.delete_table(u'main_data_readout')

        # Deleting model 'rawDataFile'
        db.delete_table(u'main_rawdatafile')

        # Deleting model 'compound'
        db.delete_table(u'main_compound')

        # Deleting model 'additional_compound_info'
        db.delete_table(u'main_additional_compound_info')

        # Deleting model 'library'
        db.delete_table(u'main_library')

        # Deleting model 'sub_library'
        db.delete_table(u'main_sub_library')


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
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'replicate': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'test': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
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