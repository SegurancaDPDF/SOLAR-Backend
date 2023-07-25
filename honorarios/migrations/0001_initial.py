# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import processo.honorarios.models


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0003_auto_20150612_1613'),
        ('contrib', '0004_auto_20150611_0956'),
        ('processo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Honorario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero_recurso_gerado', models.CharField(default=None, max_length=50, null=True, verbose_name='N\xfamero Puro Recurso', blank=True)),
                ('possivel', models.BooleanField(default=False)),
                ('situacao', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Novo'), (1, 'Recurso'), (2, 'Transitado em Julgado')])),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('data_exclusao', models.DateTimeField(default=None, null=True, verbose_name='Data de Exclus\xe3o', blank=True)),
                ('valor_estimado', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True)),
                ('valor_efetivo', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='honorarios_cadastro', default=None, to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor', models.ForeignKey(related_name='honorarios_defensor', default=None, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensoria', models.ForeignKey(related_name='honorarios_defensoria', default=None, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='honorarios_excluido', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('fase', models.OneToOneField(related_name='honorario', to='processo.Fase', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('honorario_origem', models.ForeignKey(default=None, blank=True, to='honorarios.Honorario', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'Honor\xe1io',
                'verbose_name_plural': 'Honor\xe1ios',
            },
        ),
        migrations.CreateModel(
            name='Movimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Anota\xe7\xe3o'), (1, 'Aguardando Peticionamento'), (2, 'Peti\xe7\xe3o'), (3, 'Encaminhado ao Defensor'), (4, 'Protocolo'), (5, 'Baixa')])),
                ('anotacao', models.CharField(default=None, max_length=255, null=True)),
                ('anexo', models.FileField(default=None, null=True, upload_to=processo.honorarios.models.documento_file_name, blank=True)),
                ('valor_estimado', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True)),
                ('valor_efetivo', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True)),
                ('valor_atualizado', models.DecimalField(default=None, null=True, max_digits=15, decimal_places=2, blank=True)),
                ('data_atualizacao_valor', models.DateTimeField(default=None, null=True, verbose_name='Data Atualiza\xe7\xe3o Valor', blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro')),
                ('data_exclusao', models.DateTimeField(default=None, null=True, verbose_name='Data de Exclus\xe3o', blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='movimentos_cadastro', default=None, to='contrib.Servidor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensor', models.ForeignKey(related_name='movimento_defensor', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('defensoria', models.ForeignKey(related_name='movimento_defensoria', default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('excluido_por', models.ForeignKey(related_name='movimento_excluido', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('honorario', models.ForeignKey(related_name='movimentos_honorario', default=None, to='honorarios.Honorario', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'Movimento Honor\xe1io',
                'verbose_name_plural': 'Movimentos Honor\xe1ios',
            },
        ),
    ]
