# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0029_aprisionamento_eventos'),
    ]

    operations = [
        migrations.AddField(
            model_name='mudancaregime',
            name='evento',
            field=models.ForeignKey(related_name='mudanca_regime', blank=True, editable=False, to='nadep.Historico', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
