# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tempo.django.fields


# noinspection PyPep8
class Migration(migrations.Migration):

    dependencies = [
        ('anapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NullableModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schedule', tempo.django.fields.RecurrentEventSetField(null=True, verbose_name=b'Schedule', blank=True)),
            ],
        ),
    ]
