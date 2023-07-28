# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0071_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewAtendimentoDefensor',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='ID', primary_key=True, db_column='atendimento_ptr_id')),
                ('numero', models.CharField(max_length=256, verbose_name='N\xfamero')),
                ('tipo', models.SmallIntegerField(verbose_name='Tipo', choices=[(0, 'Liga\xe7\xe3o'), (1, 'Inicial'), (2, 'Retorno'), (3, 'Recep\xe7\xe3o'), (4, 'Apoio de N\xfacleo Especializado'), (5, 'Anota\xe7\xe3o'), (6, 'Processo'), (7, 'Visita ao Preso'), (8, 'Atendimento ao Interessado'), (9, 'Encaminhamento'), (10, 'Atividade')])),
                ('data_agendamento', models.DateTimeField(verbose_name='Data do agendamento')),
                ('data_atendimento', models.DateTimeField(verbose_name='Data do atendimento')),
                ('requerente_nome', models.CharField(max_length=256, verbose_name='Requerente nome')),
                ('requerente_nome_social', models.CharField(max_length=256, verbose_name='Requerente nome social')),
                ('requerido_nome', models.CharField(max_length=256, verbose_name='Requerido nome')),
                ('requerido_nome_social', models.CharField(max_length=256, verbose_name='Requerido nome social')),
                ('agenda_id', models.IntegerField(verbose_name='Agenda ID')),
                ('inicial_id', models.IntegerField(verbose_name='Inicial ID')),
                ('inicial_numero', models.CharField(max_length=256, verbose_name='Inicial N\xfamero')),
                ('origem_id', models.IntegerField(verbose_name='Origem ID')),
                ('origem_tipo', models.SmallIntegerField(verbose_name='Tipo Origem')),
                ('recepcao_id', models.IntegerField(verbose_name='Atendimento Recep\xe7\xe3o ID')),
                ('data_atendimento_recepcao', models.DateTimeField(verbose_name='Data do atendimento da Recep\xe7\xe3o')),
                ('defensor_id', models.IntegerField(verbose_name='Defensor ID')),
                ('defensor_nome', models.CharField(max_length=256, verbose_name='Defensor nome')),
                ('substituto_id', models.IntegerField(verbose_name='Substituto ID')),
                ('substituto_nome', models.CharField(max_length=256, verbose_name='Substituto nome')),
                ('responsavel_id', models.IntegerField(verbose_name='Respons\xe1vel ID')),
                ('responsavel_nome', models.CharField(max_length=256, verbose_name='Respons\xe1vel nome')),
                ('defensoria_id', models.IntegerField(verbose_name='Defensoria ID')),
                ('defensoria_nome', models.CharField(max_length=256, verbose_name='Defensoria nome')),
                ('comarca_id', models.IntegerField(verbose_name='Comarca ID')),
                ('nucleo_id', models.IntegerField(verbose_name='N\xfacleo ID')),
                ('nucleo_nome', models.CharField(max_length=256, verbose_name='N\xfacleo nome')),
                ('area_nome', models.CharField(max_length=256, verbose_name='\xc1rea nome')),
                ('qualificacao_nome', models.CharField(max_length=256, verbose_name='Qualifica\xe7\xe3o nome')),
                ('especializado_id', models.IntegerField(verbose_name='Especializado ID')),
                ('ativo', models.BooleanField(verbose_name='Ativo')),
                ('prazo', models.BooleanField(verbose_name='Prazo')),
                ('prioridade', models.SmallIntegerField(verbose_name='Prioridade')),
                ('extra', models.BooleanField(verbose_name='Extra-Pauta')),
                ('cadastrado_por_nome', models.CharField(max_length=256, verbose_name='Cadastrado por nome')),
                ('liberado_por_nome', models.CharField(max_length=256, verbose_name='Liberado por nome')),
                ('atendido_por_nome', models.CharField(max_length=256, verbose_name='Atendido por nome')),
            ],
            options={
                'db_table': 'vw_atendimentos_defensor',
                'managed': False,
            },
        ),
    ]
