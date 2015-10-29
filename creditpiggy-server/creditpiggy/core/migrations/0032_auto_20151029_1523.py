# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20151028_1731'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignproject',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='campaignproject',
            name='project',
        ),
        migrations.AddField(
            model_name='campaign',
            name='website',
            field=models.ForeignKey(default=None, to='core.Website', null=True),
        ),
        migrations.DeleteModel(
            name='CampaignProject',
        ),
    ]
