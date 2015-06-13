# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import data.models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='csv_file',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('raw_csv_file', models.FileField(null=True, upload_to=data.models.get_file_name)),
                ('cleaned_csv_file', models.FileField(storage=data.models.OverwriteFileSystemStorage(), null=True, upload_to=b'CSV', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('library', models.CharField(max_length=50, verbose_name=b'Library')),
                ('plate_well', models.CharField(max_length=50)),
                ('plate', models.IntegerField()),
                ('well', models.CharField(max_length=20)),
                ('hit', models.PositiveSmallIntegerField(default=0, verbose_name=b'Hit')),
                ('welltype', models.CharField(default=b'X', max_length=1, choices=[(b'B', b'bad well'), (b'E', b'empty'), (b'P', b'positive control'), (b'N', b'negative control'), (b'X', b'compound')])),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('readout1', models.FloatField(null=True, blank=True)),
                ('readout2', models.FloatField(null=True, blank=True)),
                ('readout3', models.FloatField(null=True, blank=True)),
                ('readout4', models.FloatField(null=True, blank=True)),
                ('readout5', models.FloatField(null=True, blank=True)),
                ('readout6', models.FloatField(null=True, blank=True)),
                ('readout7', models.FloatField(null=True, blank=True)),
                ('readout8', models.FloatField(null=True, blank=True)),
                ('readout9', models.FloatField(null=True, blank=True)),
                ('readout10', models.FloatField(null=True, blank=True)),
                ('readout11', models.FloatField(null=True, blank=True)),
                ('readout12', models.FloatField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(default=b'Untitled', max_length=10, verbose_name=b'Project Name')),
                ('memo', models.TextField(blank=True)),
                ('meta', data.models.JSONField(null=True, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='data',
            name='project',
            field=models.ForeignKey(to='data.project'),
        ),
        migrations.AddField(
            model_name='csv_file',
            name='project',
            field=models.ForeignKey(blank=True, to='data.project', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='data',
            unique_together=set([('plate_well', 'project')]),
        ),
        migrations.AlterIndexTogether(
            name='data',
            index_together=set([('plate_well', 'project')]),
        ),
    ]
