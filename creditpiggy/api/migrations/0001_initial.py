# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0004_auto_20150211_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth_key', models.CharField(help_text=b'A unique ID used by server-side software to identify the user', max_length=64, db_index=True)),
                ('auth_salt', models.CharField(help_text=b'The salt for authenticaton checksum token', max_length=64)),
                ('auth_hash', models.CharField(help_text=b"A validation checksum hash for the secret key in the user's computer", max_length=256)),
                ('tokenType', models.CharField(default=b'', max_length=2)),
                ('user', models.ForeignKey(to='frontend.PiggyUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreditCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credit', models.IntegerField()),
                ('project', models.ForeignKey(to='frontend.ProjectRevision')),
                ('user', models.ForeignKey(to='frontend.PiggyUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectAuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tokenType', models.CharField(default=b'', max_length=2)),
                ('project', models.ForeignKey(to='frontend.Project')),
                ('token', models.ForeignKey(to='api.AuthToken')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
