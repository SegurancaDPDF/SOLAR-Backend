# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0014_auto_20160921_0842'),
        ('assistido', '0007_auto_20160928_0858'),
        ('contrib', '0007_defensoria_documentos'),
        ('nadep', '0037_auto_20160921_0842'),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculoExecucaoPenal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pessoa_nome', models.CharField(max_length=256)),
                ('execucao_numero', models.CharField(max_length=50, verbose_name='N\xfamero')),
                ('estabelecimento_penal_nome', models.CharField(max_length=200)),
                ('regime_atual', models.SmallIntegerField(verbose_name='Regime Atual', choices=[(0, 'Fechado'), (1, 'Semiaberto'), (2, 'Aberto'), (3, 'Livramento'), (4, 'Medida de Seguran\xe7a')])),
                ('data_base', models.DateField(verbose_name='Data-Base')),
                ('data_progressao', models.DateField(verbose_name='Data p/ Progress\xe3o de Regime')),
                ('data_livramento', models.DateField(verbose_name='Data p/ Livramento Condicional')),
                ('data_termino', models.DateField(verbose_name='Data do T\xe9rmino da Pena')),
                ('total_pena', models.CharField(max_length=10, verbose_name='Pena Total')),
                ('total_detracoes', models.CharField(max_length=10, verbose_name='Pena Total')),
                ('total_interrupcoes', models.CharField(max_length=10, verbose_name='Pena Total')),
                ('total_remissoes', models.CharField(max_length=10, verbose_name='Pena Total')),
                ('pena_cumprida_data_base', models.CharField(max_length=10, verbose_name='Pena Cumprida - Data Base')),
                ('pena_cumprida_data_registro', models.CharField(max_length=10, verbose_name='Pena Cumprida - Data Registro')),
                ('pena_restante_data_base', models.CharField(max_length=10, verbose_name='Pena Restante - Data Base')),
                ('pena_restante_data_registro', models.CharField(max_length=10, verbose_name='Pena Restante - Data Registro')),
                ('data_atualizacao', models.DateField(verbose_name='Data-Base')),
                ('atualizado_por_nome', models.CharField(max_length=256)),
                ('ativo', models.BooleanField(default=True)),
                ('atualizado_por', models.ForeignKey(related_name='+', to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('estabelecimento_penal', models.ForeignKey(verbose_name='Estabelecimento Penal', to='nadep.EstabelecimentoPenal', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('execucao', models.ForeignKey(related_name='calculos', to='processo.Processo', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pessoa', models.OneToOneField(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['pessoa_nome', 'data_progressao'],
                'verbose_name': 'C\xe1lculo de Execu\xe7\xe3o Penal',
                'verbose_name_plural': 'C\xe1lculos de Execu\xe7\xe3o Penal',
            },
        ),
    ]
