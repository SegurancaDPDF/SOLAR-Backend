# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0042_manifestacao_fase_perm_view_distribuicao'),
    ]

    operations = [
        migrations.AddField(
            model_name='fasetipo',
            name='codigo_cnj',
            field=models.CharField(default=None, max_length=25, blank=True, help_text='C\xf3digo Nacional do Movimento (para mais detalhes, acesse o SGT/CNJ)', null=True, verbose_name='C\xf3digo CNJ'),
        ),
        migrations.AlterField(
            model_name='fasetipo',
            name='codigo_eproc',
            field=models.CharField(default=None, max_length=25, null=True, verbose_name='C\xf3digo MNI (depreciado)', blank=True),
        ),
    ]
