# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0001_initial'),
        ('nucleo', '0001_initial'),
        ('assistido', '0002_auto_20150525_0835'),
        ('contrib', '0001_initial'),
        ('defensor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tarefa',
            name='finalizado',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='tarefa',
            name='origem',
            field=models.ForeignKey(related_name='all_respostas', default=None, blank=True, to='atendimento.Tarefa', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='tarefa',
            name='responsavel',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='resposta',
            name='atendimento',
            field=models.ForeignKey(related_name='+', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='resposta',
            name='pergunta',
            field=models.ForeignKey(to='atendimento.Pergunta', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='area',
            field=models.ForeignKey(to='contrib.Area', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='especializado',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Especializado', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='qualificacao',
            name='nucleo',
            field=models.ForeignKey(default=None, blank=True, to='nucleo.Nucleo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='procedimento',
            name='encaminhamento',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Encaminhamento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='procedimento',
            name='informacao',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Informacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='procedimento',
            name='ligacao',
            field=models.ForeignKey(related_name='ligacao', to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='atendimento',
            field=models.ForeignKey(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='pessoa',
            field=models.ForeignKey(related_name='atendimentos', to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='pergunta',
            name='qualificacao',
            field=models.ForeignKey(to='atendimento.Qualificacao', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='justificativa',
            name='atendimento',
            field=models.OneToOneField(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='cancelado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='confirmado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='defensor',
            field=models.ForeignKey(to='defensor.Defensor', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='impedimento',
            name='pessoa',
            field=models.ForeignKey(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='especializado',
            name='nucleo',
            field=models.ForeignKey(default=None, blank=True, to='nucleo.Nucleo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='encaminhamento',
            name='endereco',
            field=models.ForeignKey(to='contrib.Endereco', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='encaminhamento',
            name='telefone',
            field=models.ForeignKey(to='contrib.Telefone', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='atendimento',
            field=models.ForeignKey(blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='documento',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Documento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='documento',
            name='enviado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='cronometro',
            name='atendimento',
            field=models.ForeignKey(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='cronometro',
            name='servidor',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='coletivo',
            name='atendimento',
            field=models.OneToOneField(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='coletivo',
            name='comunidade',
            field=models.ForeignKey(default=None, blank=True, to='assistido.Pessoa', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='agendado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='atendido_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='contrib.Servidor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='inicial',
            field=models.ForeignKey(related_name='inicial+', default=None, blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='itinerante',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Itinerante', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='nucleo',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='nucleo.Nucleo', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='origem',
            field=models.ForeignKey(related_name='filhos', default=None, blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='qualificacao',
            field=models.ForeignKey(default=None, blank=True, to='atendimento.Qualificacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='remarcado',
            field=models.ForeignKey(related_name='atendimento_remarcado', default=None, blank=True, to='atendimento.Atendimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='acordo',
            name='atendimento',
            field=models.OneToOneField(to='atendimento.Atendimento', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='acordo',
            name='termo',
            field=models.ForeignKey(blank=True, to='atendimento.Documento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='procedimento',
            name='agendamento',
            field=models.ForeignKey(related_name='agendamento', default=None, blank=True, to='atendimento.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensor',
            name='defensor',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensor',
            name='defensoria',
            field=models.ForeignKey(default=None, blank=True, to='contrib.Defensoria', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensor',
            name='finalizado_por',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensor',
            name='impedimento',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='atendimento.Impedimento', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensor',
            name='responsavel',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='defensor',
            name='substituto',
            field=models.ForeignKey(related_name='+', default=None, blank=True, to='defensor.Defensor', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
