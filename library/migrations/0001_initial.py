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
                ('facility_reagent_id', models.CharField(max_length=30)),
                ('plate', models.IntegerField(default=0)),
                ('well', models.CharField(max_length=20)),
                ('plate_well', models.CharField(max_length=20)),
                ('pubchem_cid', models.IntegerField(default=0)),
                ('chemical_name', models.TextField()),
                ('molecular_weight', models.DecimalField(max_digits=10, decimal_places=5)),
                ('formula', models.CharField(max_length=30)),
                ('tpsa', models.DecimalField(max_digits=8, decimal_places=2)),
                ('logp', models.DecimalField(max_digits=8, decimal_places=4)),
                ('inchikey', models.CharField(max_length=30)),
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
                ('library_name', models.CharField(max_length=30)),
                ('number_of_sub_librarys', models.IntegerField(default=0)),
                ('number_of_compounds', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='sub_library',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sub_library_name', models.CharField(max_length=30)),
                ('number_of_compounds', models.IntegerField(default=0)),
                ('super_library', models.ForeignKey(to='library.library')),
            ],
        ),
        migrations.AddField(
            model_name='compound',
            name='library_name',
            field=models.ForeignKey(to='library.library'),
        ),
        migrations.AddField(
            model_name='compound',
            name='sub_library_name',
            field=models.ForeignKey(to='library.sub_library'),
        ),
    ]
