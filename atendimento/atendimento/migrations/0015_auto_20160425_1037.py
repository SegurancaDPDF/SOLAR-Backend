# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0014_defensor_comarca'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='atendimento',
            name='itinerante',
        ),
        migrations.DeleteModel(
            name='Itinerante',
        ),
    ]
