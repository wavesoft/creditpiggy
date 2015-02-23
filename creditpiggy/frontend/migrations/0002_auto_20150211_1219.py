# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default=b'ME', max_length=2, choices=[(b'OW', b'Owner'), (b'AD', b'Administrator'), (b'MO', b'Moderator'), (b'ME', b'Member')])),
                ('project', models.ForeignKey(to='frontend.ProjectRevision')),
                ('user', models.ForeignKey(to='frontend.PiggyUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='projectmembers',
            name='project',
        ),
        migrations.RemoveField(
            model_name='projectmembers',
            name='user',
        ),
        migrations.DeleteModel(
            name='ProjectMembers',
        ),
    ]
