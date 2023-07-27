# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0027_auto_20160428_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='eventos',
            field=models.ManyToManyField(related_name='atendimentos', editable=False, to='nadep.Historico'),
        ),
    ]
