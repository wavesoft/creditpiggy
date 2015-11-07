# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20151106_1732'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampaignAchievementInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='achievement',
            name='team',
            field=models.BooleanField(default=False, help_text=b'When used as a campaign or project achievement, grant this to each member of the campaign'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='achievements',
            field=models.ManyToManyField(to='core.Achievement', blank=True),
        ),
        migrations.AlterField(
            model_name='achievement',
            name='personal',
            field=models.BooleanField(default=False, help_text=b"This is something achieved in the user's personal metrics"),
        ),
        migrations.AddField(
            model_name='campaignachievementinstance',
            name='achievement',
            field=models.ForeignKey(to='core.Achievement'),
        ),
        migrations.AddField(
            model_name='campaignachievementinstance',
            name='campaign',
            field=models.ForeignKey(to='core.Campaign'),
        ),
    ]
