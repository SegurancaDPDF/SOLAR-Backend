# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0007_atendimento_motivo_exclusao'),
        ('contrib', '0004_auto_20150611_0956'),
        ('processo', '0002_auto_20150722_1608'),
        ('assistido', '0002_auto_20150525_0835'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atendimento',
            fields=[
                ('defensor_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='atendimento.Defensor', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('assunto', models.CharField(max_length=255, null=True, blank=True)),
                ('parentesco_preso', models.SmallIntegerField(blank=True, null=True, choices=[(1, 'Pai/M\xe3e'), (2, 'Filho/Filha'), (3, 'Irm\xe3o/Irm\xe3'), (4, 'Esposo/Esposta'), (0, 'Outro')])),
            ],
            bases=('atendimento.defensor',),
        ),
        migrations.CreateModel(
            name='EstabelecimentoPenal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro', null=True)),
                ('nome', models.CharField(max_length=200)),
                ('tipo', models.SmallIntegerField(choices=[(0, 'Delegacia'), (1, 'Pres\xeddio/Penitenci\xe1ria'), (2, 'Cadeia p\xfablica / Casa de deten\xe7\xe3o ou similares'), (3, 'Casa do albergado'), (4, 'Col\xf4nia agr\xedcola, industrial ou similar'), (5, 'Hospital de Cust\xf3dia e Tratamento Psiqui\xe1trico'), (6, 'Hospital Particular'), (7, 'Hospital P\xfablico')])),
                ('ativo', models.BooleanField(default=True)),
                ('endereco', models.ForeignKey(default=None, blank=True, to='contrib.Endereco', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('telefone', models.ForeignKey(default=None, blank=True, to='contrib.Telefone', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.CreateModel(
            name='Prisao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(blank=True, null=True, verbose_name='Tipo', choices=[(0, 'Provis\xf3rio'), (1, 'Condenado')])),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro', null=True)),
                ('data_fato', models.DateField(null=True, verbose_name='Data do Fato', blank=True)),
                ('data_prisao', models.DateField(null=True, verbose_name='Data da Pris\xe3o', blank=True)),
                ('data_termino', models.DateField(null=True, verbose_name='T\xe9rmino da Pena', blank=True)),
                ('situacao', models.SmallIntegerField(blank=True, null=True, verbose_name='Situa\xe7\xe3o', choices=[(0, 'Preso'), (1, 'Solto')])),
                ('regime_inicial', models.SmallIntegerField(blank=True, null=True, verbose_name='Regime Inicial', choices=[(0, 'Fechado'), (1, 'Semiaberto'), (2, 'Aberto'), (3, 'Livramento'), (4, 'Medida de Seguran\xe7a')])),
                ('regime_atual', models.SmallIntegerField(blank=True, null=True, verbose_name='Regime Atual', choices=[(0, 'Fechado'), (1, 'Semiaberto'), (2, 'Aberto'), (3, 'Livramento'), (4, 'Medida de Seguran\xe7a')])),
                ('duracao_pena_anos', models.SmallIntegerField(null=True, verbose_name='Dura\xe7\xe3o da Pena (Anos)', blank=True)),
                ('duracao_pena_meses', models.SmallIntegerField(null=True, verbose_name='Dura\xe7\xe3o da Pena (Meses)', blank=True)),
                ('duracao_pena_dias', models.SmallIntegerField(null=True, verbose_name='Dura\xe7\xe3o da Pena (Dias)', blank=True)),
                ('multa', models.CharField(max_length=512, null=True, verbose_name='Dias Multa', blank=True)),
                ('data_recebimento_denuncia', models.DateField(null=True, verbose_name='Data de Recebimento da Den\xfancia', blank=True)),
                ('data_pronuncia', models.DateField(null=True, verbose_name='Data da Pron\xfancia', blank=True)),
                ('data_sentenca_condenatoria', models.DateField(null=True, verbose_name='Data da Seten\xe7a Condenat\xf3ria', blank=True)),
                ('data_transito_defensor', models.DateField(null=True, verbose_name='Tr\xe2nsido em Julgado da Senten\xe7a para o Defensor', blank=True)),
                ('data_transito_acusacao', models.DateField(null=True, verbose_name='Tr\xe2nsido em Julgado da Senten\xe7a para a Acusa\xe7\xe3o', blank=True)),
                ('data_transito_apenado', models.DateField(null=True, verbose_name='Tr\xe2nsido em Julgado da Senten\xe7a para o(a) Apenado(a)', blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('estabelecimento_penal', models.ForeignKey(verbose_name='Estabelecimento Penal', to='nadep.EstabelecimentoPenal', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('local_prisao', models.ForeignKey(verbose_name='Munic\xedpio do Local da Pris\xe3o', blank=True, to='contrib.Municipio', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('parte', models.ForeignKey(related_name='prisoes', blank=True, to='processo.Parte', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pessoa', models.ForeignKey(to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('processo', models.ForeignKey(related_name='prisoes', blank=True, to='processo.Processo', null=True, on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.CreateModel(
            name='Tipificacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de cadastro', null=True)),
                ('nome', models.CharField(max_length=512)),
                ('ativo', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='prisao',
            name='tipificacao',
            field=models.ForeignKey(verbose_name='Tipifica\xe7\xe3o', blank=True, to='nadep.Tipificacao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='prisao',
            field=models.ForeignKey(blank=True, to='nadep.Prisao', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
