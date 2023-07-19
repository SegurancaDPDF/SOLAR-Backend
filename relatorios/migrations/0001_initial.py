# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Relatorios',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'permissions': (('view_relat_atividades', 'Can view relatorio atividades comarca ou diretoria'), ('view_relat_atendimentos_defensor', 'Can view relatorio atendimentos do defensor'), ('view_relat_atendimentos_substitutos', 'Can view relatorio atendimentos dos substitutos'), ('view_relat_plantao_periodo', 'Can view relatorio atividades do defensor'), ('view_relat_plantao_periodo_defensor', 'Can view relatorio atividades do defensor no periodo'), ('view_relat_processo_fase_acumulacao', 'Can view relatorio fases proc no periodo'), ('view_relat_processo_fase_substituicao', 'Can view relatorio fases proc no periodo')),
            },
        ),
    ]
