# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0019_arvore_ativo'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pessoa',
            unique_together=set([('atendimento', 'pessoa')]),
        ),
    ]
