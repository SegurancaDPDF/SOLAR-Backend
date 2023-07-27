# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0028_atendimento_eventos'),
    ]

    operations = [
        migrations.AddField(
            model_name='aprisionamento',
            name='eventos',
            field=models.ManyToManyField(related_name='aprisionamentos', editable=False, to='nadep.Historico'),
        ),
    ]
