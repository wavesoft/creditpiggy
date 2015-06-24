# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150624_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisualMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', help_text=b'The code name of the metric', max_length=200)),
                ('display_name', models.CharField(default=b'', help_text=b"How it's displayed to the user", max_length=200)),
                ('icon', models.CharField(default=b'', help_text=b'Metric icon (from fontawesome)', max_length=200)),
                ('units', models.CharField(default=b'', help_text=b'Metric units', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='piggyproject',
            name='visual_metrics',
            field=models.ManyToManyField(to='core.VisualMetric', blank=True),
        ),
        migrations.AddField(
            model_name='website',
            name='visual_metrics',
            field=models.ManyToManyField(to='core.VisualMetric', blank=True),
        ),
    ]
