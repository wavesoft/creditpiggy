# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_website_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('subject', models.CharField(default=b'', max_length=512)),
                ('body', tinymce.models.HTMLField(help_text=b'The e-mail body')),
                ('sent_date', models.DateTimeField(default=None, null=True, editable=False)),
                ('draft', models.BooleanField(default=True, help_text=b'Uncheck this to send the e-mail')),
                ('target_campaign', models.ManyToManyField(to='core.Campaign', blank=True)),
                ('target_project', models.ManyToManyField(to='core.PiggyProject', blank=True)),
                ('target_user', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
    ]
