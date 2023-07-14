# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0045_distribuicao_por_polo_e_competencia'),
        ('procapi_client', '0007_tipo_evento'),
        ('contrib', '0050_defensoriavara_distribuicao_automatica'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoriavara',
            name='distribuir_por_competencia',
            field=models.ManyToManyField(default=None, to='procapi_client.Competencia', verbose_name='Distribuir Avisos Por Determinada Compet\xeancia', blank=True),
        ),
        migrations.AddField(
            model_name='defensoriavara',
            name='distribuir_por_polo',
            field=models.ManyToManyField(default=None, to='processo.ProcessoPoloDestinatario', verbose_name='Distribuir Avisos Por Determinado Polo do Destinat\xe1rio', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='defensoriavara',
            unique_together=set([]),
        ),
    ]
