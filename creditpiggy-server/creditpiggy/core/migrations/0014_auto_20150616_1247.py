# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
import creditpiggy.core.metrics


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_piggyprojectgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', help_text=b'Name of the website', max_length=200)),
                ('desc', tinymce.models.HTMLField(help_text=b'Short description')),
                ('icon', models.CharField(default=b'', max_length=200)),
                ('projects', models.ManyToManyField(to='core.PiggyProject')),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='piggyprojectgroup',
            name='projects',
        ),
        migrations.RemoveField(
            model_name='projectcredentials',
            name='project',
        ),
        migrations.DeleteModel(
            name='PiggyProjectGroup',
        ),
        migrations.DeleteModel(
            name='ProjectCredentials',
        ),
    ]
