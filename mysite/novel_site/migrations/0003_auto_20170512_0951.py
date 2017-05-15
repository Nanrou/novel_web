# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-12 01:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('novel_site', '0002_infotable_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='booktableone',
            name='book_id',
            field=models.IntegerField(null=True, verbose_name='book_id'),
        ),
        migrations.AddField(
            model_name='booktablethree',
            name='book_id',
            field=models.IntegerField(null=True, verbose_name='book_id'),
        ),
        migrations.AddField(
            model_name='booktabletwo',
            name='book_id',
            field=models.IntegerField(null=True, verbose_name='book_id'),
        ),
        migrations.AddField(
            model_name='infotable',
            name='resume',
            field=models.CharField(max_length=300, null=True),
        ),
    ]