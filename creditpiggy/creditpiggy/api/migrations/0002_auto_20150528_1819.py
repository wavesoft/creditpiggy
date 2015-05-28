# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectauthtoken',
            name='project',
            field=models.ForeignKey(to='frontend.Project'),
        ),
        migrations.AddField(
            model_name='projectauthtoken',
            name='token',
            field=models.ForeignKey(to='api.AuthToken'),
        ),
        migrations.AddField(
            model_name='creditcache',
            name='project',
            field=models.ForeignKey(to='frontend.ProjectRevision'),
        ),
        migrations.AddField(
            model_name='creditcache',
            name='user',
            field=models.ForeignKey(to='frontend.PiggyUser'),
        ),
        migrations.AddField(
            model_name='authtoken',
            name='user',
            field=models.ForeignKey(to='frontend.PiggyUser'),
        ),
    ]
