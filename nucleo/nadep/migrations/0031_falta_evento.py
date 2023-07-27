# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0030_mudancaregime_evento'),
    ]

    operations = [
        migrations.AddField(
            model_name='falta',
            name='evento',
            field=models.ForeignKey(related_name='falta', blank=True, editable=False, to='nadep.Historico', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
