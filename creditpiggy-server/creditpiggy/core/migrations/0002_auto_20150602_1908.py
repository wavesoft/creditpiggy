# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time
import creditpiggy.core.metrics
import tinymce.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', help_text=b'Name of the achievement', max_length=200)),
                ('desc', tinymce.models.HTMLField(help_text=b'Achievement short text')),
                ('v_icon', models.CharField(default=b'', max_length=200)),
                ('v_color', models.CharField(default=b'#662D91', max_length=24)),
                ('v_frame', models.CharField(default=b'circle', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', help_text=b'Name of the campaign', max_length=200)),
                ('desc', tinymce.models.HTMLField(help_text=b'Campaign description')),
                ('start_time', models.IntegerField(default=time.time)),
                ('end_time', models.IntegerField(default=time.time)),
                ('published', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='CampaignAchievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achievement', models.ForeignKey(to='core.Achievement')),
                ('campaign', models.ForeignKey(to='core.Campaign')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectAchievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achievement', models.ForeignKey(to='core.Achievement')),
            ],
        ),
        migrations.CreateModel(
            name='UserAchievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achievement', models.ForeignKey(to='core.Achievement')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RenameField(
            model_name='piggyproject',
            old_name='profileImage',
            new_name='profile_image',
        ),
        migrations.AlterField(
            model_name='piggyproject',
            name='desc',
            field=tinymce.models.HTMLField(help_text=b'Project description'),
        ),
        migrations.AddField(
            model_name='projectachievement',
            name='project',
            field=models.ForeignKey(to='core.PiggyProject'),
        ),
    ]
