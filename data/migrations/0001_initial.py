# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='csv_file',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('project_id', models.CharField(max_length=50, null=True, verbose_name=b'Project ID', blank=True)),
                ('session_id', models.CharField(max_length=50, null=True, verbose_name=b'Session ID', blank=True)),
                ('raw_csv_file', models.FileField(null=True, upload_to=b'')),
                ('cleaned_csv_file', models.FileField(null=True, upload_to=b'', blank=True)),
                ('create_by', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
