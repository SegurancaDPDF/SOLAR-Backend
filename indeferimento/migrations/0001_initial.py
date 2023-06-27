# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0009_auto_20180510_1526'),
        ('atendimento', '0051_impedimento_anotacao_comunicacao'),
        ('assistido', '0016_pessoa_tipo_cadastro'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Indeferimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medida_pretendida', models.TextField(null=True, blank=True)),
                ('justificativa', models.TextField(null=True, blank=True)),
                ('resultado', models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'N\xe3o Avaliado'), (10, 'Deferido'), (20, 'Indeferido')])),
                ('tipo_baixa', models.SmallIntegerField(default=0, null=True, blank=True, choices=[(0, 'N\xe3o Realizada'), (10, 'Retorno Marcado'), (20, 'Encaminhamento Marcado'), (30, 'Atendimento Negado')])),
                ('atendimento', models.ForeignKey(related_name='indeferimentos', on_delete=django.db.models.deletion.DO_NOTHING, to='atendimento.Defensor')),
                ('defensor', models.ForeignKey(related_name='indeferimentos', on_delete=django.db.models.deletion.DO_NOTHING, to='defensor.Defensor')),
                ('pessoa', models.ForeignKey(related_name='indeferimentos', on_delete=django.db.models.deletion.DO_NOTHING, to='assistido.PessoaAssistida')),
                ('processo', models.OneToOneField(related_name='indeferimento', on_delete=django.db.models.deletion.DO_NOTHING, to='core.Processo')),
            ],
        ),
    ]
