# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0015_auto_20170816_1445'),
        ('djdocuments', '0011_todos_modelo_pronto_para_utilizacao_como_true'),
        ('atendimento', '0047_auto_20180118_1131'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModeloDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=255)),
                ('tipo', models.PositiveSmallIntegerField(default=0, choices=[(0, 'GED'), (1, 'Jasper')])),
                ('jasper_resource', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('jasper_name', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('jasper_params', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('ativo', models.BooleanField(default=True)),
                ('cadastrado_por', models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.AlterModelOptions(
            name='impedimento',
            options={'ordering': ['-ativo', 'data_cadastro', 'pessoa__nome', 'defensor']},
        ),
        migrations.RemoveField(
            model_name='impedimento',
            name='cancelado_por',
        ),
        migrations.RemoveField(
            model_name='impedimento',
            name='confirmado_por',
        ),
        migrations.RemoveField(
            model_name='impedimento',
            name='data_cancelado',
        ),
        migrations.RemoveField(
            model_name='impedimento',
            name='data_confirmado',
        ),
        migrations.AddField(
            model_name='documento',
            name='impedimento',
            field=models.ForeignKey(related_name='documentos_avaliacao', blank=True, to='atendimento.Impedimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='anotacao_avaliacao',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='anotacao_baixa',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='atendimento',
            field=models.ForeignKey(related_name='impedimentos', default=None, to='atendimento.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='avaliado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='baixado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='cadastrado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='data_avaliacao',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='data_baixa',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='data_cadastro',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='data_recurso',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='medida_pretendida',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='razao',
            field=models.ForeignKey(related_name='+', default=None, to='atendimento.Qualificacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='recorrido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='resultado',
            field=models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'N\xe3o Avaliado'), (10, 'Deferido'), (20, 'Indeferido')]),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='tipo_baixa',
            field=models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'N\xe3o Realizada'), (10, 'Retorno Marcado'), (20, 'Encaminhamento Marcado'), (30, 'Atendimento Negado')]),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='impedimento',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_DEFAULT, default=None, blank=True, to='atendimento.Impedimento', null=True),
        ),
        migrations.AlterField(
            model_name='impedimento',
            name='justificativa',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='impedimento',
            name='pessoa',
            field=models.ForeignKey(related_name='impedimentos', to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='qualificacao',
            name='tipo',
            field=models.PositiveSmallIntegerField(default=10, choices=[(10, 'Pedido'), (20, 'Atividade'), (30, 'Impedimento'), (40, 'Suspei\xe7\xe3o'), (50, 'Nega\xe7\xe3o'), (51, 'Nega\xe7\xe3o por Hipossufici\xeancia')]),
        ),
        migrations.AddField(
            model_name='modelodocumento',
            name='ged_modelo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Documento', blank=True, to='djdocuments.Documento', null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='modelo',
            field=models.ForeignKey(related_name='modelo', blank=True, to='atendimento.ModeloDocumento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='modelos_documentos',
            field=models.ManyToManyField(related_name='qualificacoes', to='atendimento.ModeloDocumento', blank=True),
        ),
    ]
