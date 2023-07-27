# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nadep', '0005_aprisionamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='estabelecimento_penal',
            field=models.ForeignKey(blank=True, to='nadep.EstabelecimentoPenal', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
