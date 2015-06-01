# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import creditpiggy.core.metrics


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_projectusercredits_claimed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectUserCredit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credits', models.IntegerField(default=0)),
                ('claimed', models.BooleanField(default=False)),
                ('project', models.ForeignKey(to='core.PiggyProject')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            bases=(creditpiggy.core.metrics.MetricsModelMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='projectusercredits',
            name='project',
        ),
        migrations.RemoveField(
            model_name='projectusercredits',
            name='user',
        ),
        migrations.DeleteModel(
            name='ProjectUserCredits',
        ),
    ]
