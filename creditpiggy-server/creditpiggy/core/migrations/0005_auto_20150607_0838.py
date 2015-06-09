# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150603_2138'),
    ]

    operations = [
        migrations.CreateModel(
            name='AchievementInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.IntegerField(default=0)),
                ('achievement', models.ForeignKey(to='core.Achievement')),
                ('campaign', models.ForeignKey(default=None, blank=True, to='core.Campaign', null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='awardedusercampaignachievement',
            name='achievement',
        ),
        migrations.RemoveField(
            model_name='awardedusercampaignachievement',
            name='user',
        ),
        migrations.RemoveField(
            model_name='awardeduserprojectachievement',
            name='achievement',
        ),
        migrations.RemoveField(
            model_name='awardeduserprojectachievement',
            name='user',
        ),
        migrations.RemoveField(
            model_name='campaignachievement',
            name='achievement',
        ),
        migrations.RemoveField(
            model_name='campaignachievement',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='projectachievement',
            name='achievement',
        ),
        migrations.RemoveField(
            model_name='projectachievement',
            name='project',
        ),
        migrations.AddField(
            model_name='campaignusercredit',
            name='achievements',
            field=models.ManyToManyField(to='core.Achievement'),
        ),
        migrations.AddField(
            model_name='piggyproject',
            name='achievements',
            field=models.ManyToManyField(to='core.Achievement'),
        ),
        migrations.DeleteModel(
            name='AwardedUserCampaignAchievement',
        ),
        migrations.DeleteModel(
            name='AwardedUserProjectAchievement',
        ),
        migrations.DeleteModel(
            name='CampaignAchievement',
        ),
        migrations.DeleteModel(
            name='ProjectAchievement',
        ),
        migrations.AddField(
            model_name='achievementinstance',
            name='project',
            field=models.ForeignKey(to='core.PiggyProject'),
        ),
        migrations.AddField(
            model_name='achievementinstance',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
