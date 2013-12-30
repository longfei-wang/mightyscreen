# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'proj_5'
        db.create_table(u'data_proj_5', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('library', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('plate', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('well', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('welltype', self.gf('django.db.models.fields.CharField')(default='X', max_length=1)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.project'])),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.submission'])),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('create_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('FP_A', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('FI_A', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('PC_A', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('SC_A', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('zscore', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'data', ['proj_5'])


        # Changing field 'proj_1.zscore'
        db.alter_column(u'data_proj_1', 'zscore', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'proj_2.zscore'
        db.alter_column(u'data_proj_2', 'zscore', self.gf('django.db.models.fields.FloatField')())

        # Changing field 'proj_4.zscore'
        db.alter_column(u'data_proj_4', 'zscore', self.gf('django.db.models.fields.FloatField')())

    def backwards(self, orm):
        # Deleting model 'proj_5'
        db.delete_table(u'data_proj_5')


        # Changing field 'proj_1.zscore'
        db.alter_column(u'data_proj_1', 'zscore', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'proj_2.zscore'
        db.alter_column(u'data_proj_2', 'zscore', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'proj_4.zscore'
        db.alter_column(u'data_proj_4', 'zscore', self.gf('django.db.models.fields.FloatField')(null=True))

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
        u'data.proj_1': {
            'FI_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FI_B': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_B': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'Meta': {'object_name': 'proj_1'},
            'PC_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'PC_B': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_B': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'create_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'welltype': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '1'}),
            'zscore': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'data.proj_2': {
            'FI_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FI_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'Meta': {'object_name': 'proj_2'},
            'PC_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'PC_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'create_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'welltype': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '1'}),
            'zscore': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'data.proj_3': {
            'FI_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FI_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'Meta': {'object_name': 'proj_3'},
            'PC_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'PC_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_1': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_2': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'create_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'welltype': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '1'})
        },
        u'data.proj_4': {
            'FI_3': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FI_4': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_3': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_4': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'Meta': {'object_name': 'proj_4'},
            'PC_3': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'PC_4': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_3': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_4': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'create_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'welltype': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '1'}),
            'zscore': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'data.proj_5': {
            'FI_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'FP_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'Meta': {'object_name': 'proj_5'},
            'PC_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'SC_A': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'create_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.submission']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'welltype': ('django.db.models.fields.CharField', [], {'default': "'X'", 'max_length': '1'}),
            'zscore': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'main.experiment': {
            'Meta': {'object_name': 'experiment'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'readout': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['main.readout']", 'symmetrical': 'False'})
        },
        u'main.plate': {
            'Meta': {'object_name': 'plate'},
            'columns': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'numofwells': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'rows': ('django.db.models.fields.TextField', [], {})
        },
        u'main.project': {
            'Meta': {'object_name': 'project'},
            'agreement': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'experiment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.experiment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'leader'", 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.plate']"}),
            'replicate': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'score': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['main.score']", 'symmetrical': 'False', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        },
        u'main.readout': {
            'Meta': {'object_name': 'readout'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'main.score': {
            'Meta': {'object_name': 'score'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'formular': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'main.submission': {
            'Meta': {'object_name': 'submission'},
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobtype': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['main.project']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submit_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'submit_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['data']