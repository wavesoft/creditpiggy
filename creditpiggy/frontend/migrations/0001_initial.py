# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PiggyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'A short identifier for the project', unique=True, max_length=50)),
                ('display_name', models.CharField(help_text=b"Project's full name", max_length=200)),
                ('contact', models.CharField(help_text=b'The associated website for this project', max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectMembers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default=b'ME', max_length=2, choices=[(b'OW', b'Owner'), (b'AD', b'Administrator'), (b'MO', b'Moderator'), (b'ME', b'Member')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revision', models.IntegerField()),
                ('project_text', models.TextField()),
                ('website', models.CharField(help_text=b'The associated website for this project', max_length=500)),
                ('project', models.ForeignKey(to='frontend.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='projectmembers',
            name='project',
            field=models.ForeignKey(to='frontend.ProjectRevision'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectmembers',
            name='user',
            field=models.ForeignKey(to='frontend.PiggyUser'),
            preserve_default=True,
        ),
    ]
