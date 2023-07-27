# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0035_aprisionamento_detracao'),
    ]

    operations = [
        migrations.AddField(
            model_name='remissao',
            name='falta',
            field=models.ForeignKey(related_name='remissoes', blank=True, editable=False, to='nadep.Falta', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
