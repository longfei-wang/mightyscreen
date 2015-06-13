# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='compound',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sub_library_name', models.CharField(max_length=100)),
                ('facility_reagent_id', models.CharField(max_length=100)),
                ('plate', models.IntegerField()),
                ('well', models.CharField(max_length=20)),
                ('plate_well', models.CharField(unique=True, max_length=20)),
                ('pubchem_cid', models.IntegerField(null=True)),
                ('chemical_name', models.TextField()),
                ('molecular_weight', models.DecimalField(max_digits=10, decimal_places=5)),
                ('formula', models.CharField(max_length=100)),
                ('tpsa', models.DecimalField(max_digits=8, decimal_places=2)),
                ('logp', models.DecimalField(max_digits=8, decimal_places=4)),
                ('inchikey', models.CharField(max_length=100)),
                ('canonical_smiles', models.TextField()),
                ('inchi', models.TextField()),
                ('fp2', models.TextField()),
                ('fp3', models.CharField(max_length=50)),
                ('fp4', models.TextField()),
                ('svg', models.TextField(verbose_name=b'Structure')),
                ('sdf', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='library',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('library_name', models.CharField(unique=True, max_length=100)),
                ('number_of_compounds', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='compound',
            name='library_name',
            field=models.ForeignKey(to='library.library'),
        ),
    ]
