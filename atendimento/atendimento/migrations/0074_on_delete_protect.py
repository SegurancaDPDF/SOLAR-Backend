# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0073_tarefa_setor_resposavel_blank_false'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='agendado_por',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Servidor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='atendido_por',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Servidor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='inicial',
            field=models.ForeignKey(
                related_name='retorno',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='atendimento.Atendimento',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='nucleo',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='nucleo.Nucleo',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='origem',
            field=models.ForeignKey(
                related_name='filhos',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='atendimento.Atendimento',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='qualificacao',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='atendimento.Qualificacao',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='remarcado',
            field=models.ForeignKey(
                related_name='atendimento_remarcado',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='atendimento.Atendimento',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='comarca',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Comarca',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='defensor',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='defensor.Defensor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='defensoria',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Defensoria',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='distribuido_por',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Servidor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='encaminhado_para',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='contrib.Defensoria',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='finalizado_por',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='defensor.Defensor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='responsavel',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='defensor.Defensor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='defensor',
            name='substituto',
            field=models.ForeignKey(
                related_name='+',
                on_delete=django.db.models.deletion.PROTECT,
                default=None,
                blank=True,
                to='defensor.Defensor',
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='atendimento',
            field=models.ForeignKey(
                related_name='partes',
                on_delete=django.db.models.deletion.PROTECT,
                to='atendimento.Atendimento'
            ),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='pessoa',
            field=models.ForeignKey(
                related_name='atendimentos',
                on_delete=django.db.models.deletion.PROTECT,
                to='assistido.PessoaAssistida'
            ),
        ),
    ]
