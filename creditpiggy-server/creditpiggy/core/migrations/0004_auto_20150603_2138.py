# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import creditpiggy.core.metrics


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_piggyproject_project_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwardedUserCampaignAchievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achieved_at', models.IntegerField(default=None, null=True)),
                ('achievement', models.ForeignKey(to='core.CampaignAchievement')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AwardedUserProjectAchievement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('achieved_at', models.IntegerField(default=None, null=True)),
                ('achievement', models.ForeignKey(to='core.ProjectAchievement')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign', models.ForeignKey(to='core.Campaign')),
            ],
        ),
        migrations.CreateModel(
            name='CampaignUserCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credits', models.IntegerField(default=0)),
                ('campaign', models.ForeignKey(to='core.Campaign')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='userachievement',
            name='achievement',
        ),
        migrations.RemoveField(
            model_name='userachievement',
            name='user',
        ),
        migrations.RenameField(
            model_name='achievement',
            old_name='v_color',
            new_name='color',
        ),
        migrations.RenameField(
            model_name='achievement',
            old_name='v_frame',
            new_name='frame_type',
        ),
        migrations.RenameField(
            model_name='achievement',
            old_name='v_icon',
            new_name='icon',
        ),
        migrations.AddField(
            model_name='achievement',
            name='expires',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='achievement',
            name='instances',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='achievement',
            name='metrics',
            field=models.TextField(default=b'{}'),
        ),
        migrations.AlterField(
            model_name='creditslot',
            name='credits',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='creditslot',
            name='maxBound',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='creditslot',
            name='minBound',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='creditslot',
            name='reason',
            field=models.CharField(default=None, max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='piggyproject',
            name='project_url',
            field=models.URLField(default=b'', blank=True),
        ),
        migrations.DeleteModel(
            name='UserAchievement',
        ),
        migrations.AddField(
            model_name='campaignproject',
            name='project',
            field=models.ForeignKey(to='core.PiggyProject'),
        ),
    ]
