# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0014_auto_20160921_0842'),
        ('nadep', '0036_remissao_falta'),
    ]

    operations = [
        migrations.AddField(
            model_name='falta',
            name='estabelecimento_penal',
            field=models.ForeignKey(blank=True, to='nadep.EstabelecimentoPenal', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='falta',
            name='processo',
            field=models.OneToOneField(null=True, blank=True, to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
