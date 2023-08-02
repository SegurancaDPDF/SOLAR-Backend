# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0012_auto_20170821_1136'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerfilCamposObrigatorios',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=256)),
                ('tipo_processo', models.SmallIntegerField(default=None, null=True, verbose_name='Tipo Processo', blank=True, choices=[(None, 'Todos'), (1, 'Atendimento'), (2, 'Processo')])),
                ('tipo_parte', models.SmallIntegerField(default=None, null=True, verbose_name='Tipo Parte', blank=True, choices=[(None, 'Todas'), (1, 'Requerente'), (2, 'Requerido')])),
                ('parte_principal', models.BooleanField(default=None, null=True, verbose_name='Parte Principal?')),
                ('configuracao', models.TextField(verbose_name='Configura\xe7\xe3o')),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Perfil de Campos Obrigat\xf3rios',
                'verbose_name_plural': 'Perfis de Campos Obrigat\xf3rios',
            },
        ),
        migrations.AlterField(
            model_name='moradia',
            name='tipo',
            field=models.SmallIntegerField(verbose_name='Im\xf3vel', choices=[(0, 'Pr\xf3prio'), (1, 'Programa Habitacional (Doa\xe7\xe3o do Gov: Federal, Estadual ou Municipal)'), (2, 'Alugado'), (3, 'Cedido'), (4, 'Financiado')]),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='tem_imoveis',
            field=models.BooleanField(default=False, verbose_name='Possui Im\xf3veis'),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='tem_investimentos',
            field=models.BooleanField(default=False, verbose_name='Possui Investimentos'),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='tem_moveis',
            field=models.BooleanField(default=False, verbose_name='Possui M\xf3veis'),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='valor_imoveis',
            field=models.DecimalField(default=0, help_text='Valor total, em R$, dos bens im\xf3veis', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='valor_investimentos',
            field=models.DecimalField(default=0, help_text='Valor total, em R$, dos investimentos', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='patrimonio',
            name='valor_moveis',
            field=models.DecimalField(default=0, help_text='Valor total, em R$, dos bens m\xf3veis', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='cpf',
            field=models.CharField(default=None, max_length=32, blank=True, null=True, verbose_name='CPF', db_index=True),
        ),
        migrations.AlterField(
            model_name='pessoa',
            name='sexo',
            field=models.SmallIntegerField(default=None, null=True, verbose_name='G\xeanero', blank=True, choices=[(0, 'Masculino'), (1, 'Feminino')]),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='naturalidade_estado',
            field=models.CharField(max_length=128, null=True, verbose_name='Naturalidade (UF)', blank=True),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='naturalidade_pais',
            field=models.ForeignKey(verbose_name='Pa\xeds de Origem', blank=True, to='contrib.Pais', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='pne',
            field=models.BooleanField(default=False, verbose_name='Portador de Necessidades Especiais (PNE)'),
        ),
        migrations.AlterField(
            model_name='pessoaassistida',
            name='raca',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Cor/Ra\xe7a', choices=[(0, 'Preta'), (1, 'Parda'), (2, 'Branca'), (3, 'Amarela'), (4, 'Ind\xedgena'), (5, 'N\xe3o soube responder')]),
        ),
        migrations.AlterField(
            model_name='renda',
            name='ganho_mensal',
            field=models.DecimalField(default=0, help_text='Ganhos mensais, em R$, do declarante', verbose_name='Renda Individual', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='renda',
            name='ganho_mensal_membros',
            field=models.DecimalField(default=0, help_text='Ganhos mensais, em R$, da entidade familiar', verbose_name='Renda Familiar', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='renda',
            name='numero_dependentes',
            field=models.SmallIntegerField(default=0, verbose_name='N\xba Dependentes'),
        ),
        migrations.AlterField(
            model_name='renda',
            name='numero_membros',
            field=models.SmallIntegerField(default=0, help_text='N\xfamero de membros na entidade familiar', verbose_name='N\xba Membros'),
        ),
        migrations.AlterField(
            model_name='renda',
            name='tem_plano_saude',
            field=models.BooleanField(default=False, verbose_name='Plano de Sa\xfade'),
        ),
        migrations.AlterUniqueTogether(
            name='perfilcamposobrigatorios',
            unique_together=set([('tipo_processo', 'tipo_parte', 'parte_principal')]),
        ),
    ]
