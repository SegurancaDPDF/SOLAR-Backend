# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0010_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='agenda',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, 'Geral'), (1, 'Concilia\xe7\xe3o (Fam\xedlia)'), (2, 'Concilia\xe7\xe3o (C\xedvel)'), (3, 'Media\xe7\xe3o')]),
        ),
    ]
