# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0005_area_penal'),
        ('honorarios', '0009_honorario_baixado'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertaProcessoMovimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mensagem', models.CharField(default=None, max_length=255, null=True, verbose_name='Mensagem alerta', blank=True)),
                ('visualizado_por_nome', models.CharField(default=None, max_length=255, null=True, verbose_name='Nome de quem visualizou', blank=True)),
                ('data_visualizado', models.DateTimeField(null=True, verbose_name='Data de visualizacao', blank=True)),
                ('visualizado', models.BooleanField(default=False)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('ativo', models.BooleanField(default=True)),
                ('honorario', models.ForeignKey(related_name='alertas', to='honorarios.Honorario', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('visualizado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['-ativo', 'data_cadastro'],
                'verbose_name': 'Alerta de Movimentacao Honorario',
                'verbose_name_plural': 'Alertas de Movimenta\xe7\xf5es Honorarios',
            },
        ),
    ]
