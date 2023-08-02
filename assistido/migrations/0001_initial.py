# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Bibliotecas de terceiros
from django.db import migrations, models
import django.db.models.deletion

# Solar
import assistido.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arquivo', models.FileField(upload_to=assistido.models.documento_file_name, verbose_name='Arquivo')),
                ('nome', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('data_enviado', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-ativo', 'pessoa__nome', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='EstruturaMoradia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Filiacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=256)),
                ('tipo', models.SmallIntegerField(choices=[(0, 'M\xe3e biol\xf3gica'), (1, 'Pai biol\xf3gico'), (2, 'M\xe3e adotiva'), (3, 'Pai adotivo')])),
                ('nome_soundex', models.CharField(max_length=256, null=True, blank=True)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Filia\xe7\xe3o',
                'verbose_name_plural': 'Filia\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Imovel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pagamento', models.SmallIntegerField(choices=[(0, 'Financiado'), (1, 'Quitado')])),
                ('banco', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('parcelas', models.SmallIntegerField()),
                ('valor_parcela', models.DecimalField(max_digits=16, decimal_places=2)),
                ('valor_total', models.DecimalField(max_digits=16, decimal_places=2)),
                ('uso_proprio', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Moradia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(choices=[(0, 'Pr\xf3prio'), (1, 'Programa Habitacional (Doa\xe7\xe3o do Gov: Federal, Estadual ou Municipal)'), (2, 'Alugado'), (3, 'Cedido'), (4, 'Financiado')])),
                ('num_comodos', models.SmallIntegerField(default=1, null=True, verbose_name='N\xba c\xf4modos', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Movel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marca', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('modelo', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('pagamento', models.SmallIntegerField(choices=[(0, 'Financiado'), (1, 'Quitado')])),
                ('banco', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('parcelas', models.SmallIntegerField()),
                ('valor_parcela', models.DecimalField(max_digits=16, decimal_places=2)),
                ('valor_total', models.DecimalField(max_digits=16, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Patrimonio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tem_imoveis', models.BooleanField(default=False)),
                ('quantidade_imoveis', models.SmallIntegerField(default=0)),
                ('valor_imoveis', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_moveis', models.BooleanField(default=False)),
                ('quantidade_moveis', models.SmallIntegerField(default=0)),
                ('valor_moveis', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_outros_bens', models.BooleanField(default=False)),
                ('valor_outros_bens', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_investimentos', models.BooleanField(default=False)),
                ('valor_investimentos', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Pessoa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=256)),
                ('apelido', models.CharField(default=None, max_length=32, null=True, blank=True)),
                ('data_nascimento', models.DateField(default=None, null=True, verbose_name='Data de nascimento', blank=True)),
                ('sexo', models.SmallIntegerField(default=None, null=True, verbose_name='Sexo', blank=True, choices=[(0, 'Masculino'), (1, 'Feminino')])),
                ('cpf', models.CharField(default=None, max_length=32, null=True, blank=True)),
                ('rg_numero', models.CharField(default=None, max_length=32, null=True, verbose_name='N\xba RG', blank=True)),
                ('rg_orgao', models.CharField(max_length=32, null=True, verbose_name='Org\xe3o RG', blank=True)),
                ('email', models.EmailField(default=None, max_length=128, null=True, blank=True)),
                ('tipo', models.SmallIntegerField(default=0, null=True, verbose_name='Tipo', blank=True, choices=[(0, 'Pessoa F\xedsica'), (1, 'Pessoa Jur\xeddica')])),
                ('nome_soundex', models.CharField(max_length=256, null=True, blank=True)),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Profissao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.CharField(max_length=32)),
                ('nome', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name': 'Profiss\xe3o',
                'verbose_name_plural': 'Profiss\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Renda',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('numero_membros', models.SmallIntegerField(default=0)),
                ('numero_dependentes', models.SmallIntegerField(default=0)),
                ('ganho_mensal', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('ganho_mensal_membros', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_gastos_tratamento', models.BooleanField(default=False)),
                ('valor_tratamento', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_plano_saude', models.BooleanField(default=False)),
                ('nome_plano_saude', models.CharField(default=None, max_length=255, null=True, blank=True)),
                ('valor_nome_saude', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_beneficio_assistencial', models.BooleanField(default=False)),
                ('valor_beneficio_assistencial', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('tem_educacao_particular_filhos', models.BooleanField(default=False)),
                ('valor_educacao_particular_filhos', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('declarante_ir', models.BooleanField(default=False)),
                ('isento_ir', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Semovente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.SmallIntegerField(choices=[(1, 'Bovino'), (2, 'Ovino'), (3, 'Su\xedno'), (4, 'Caprino'), (5, 'Equino')])),
                ('quantidade', models.SmallIntegerField()),
                ('valor_aproximado', models.DecimalField(max_digits=16, decimal_places=2)),
                ('patrimonio', models.ForeignKey(related_name='semoventes', to='assistido.Patrimonio', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
        ),
        migrations.CreateModel(
            name='PessoaAssistida',
            fields=[
                ('pessoa_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='assistido.Pessoa', on_delete=django.db.models.deletion.DO_NOTHING)),
                ('pne', models.BooleanField()),
                ('idoso', models.BooleanField()),
                ('falecido', models.BooleanField()),
                ('preso', models.BooleanField()),
                ('estado_civil', models.SmallIntegerField(blank=True, null=True, verbose_name='Estado Civil', choices=[(0, 'Solteiro(a)'), (1, 'Casado(a)'), (2, 'Viuvo(a)'), (3, 'Divorciado(a)'), (4, 'Uni\xe3o est\xe1vel')])),
                ('qtd_filhos', models.SmallIntegerField(null=True, verbose_name='Qtd. Filhos', blank=True)),
                ('qtd_pessoas', models.SmallIntegerField(help_text='Quantidade de pessoas que morando junto, incluido assistido', null=True, verbose_name='Qtd. Pessoas', blank=True)),
                ('escolaridade', models.SmallIntegerField(blank=True, null=True, verbose_name='Escolaridade', choices=[(0, 'Nenhuma (Analfabeto)'), (1, 'Fundamental Incompleto. (1\xb0 ao 9\xb0 ano)'), (2, 'Fundamental Completo. (1\xb0 ao 9\xb0 ano)'), (3, 'M\xe9dio Incompleto. (2\xb0grau)'), (4, 'M\xe9dio Completo. (2\xb0 grau)'), (5, 'Superior Incompleto'), (6, 'Superior Completo'), (7, 'P\xf3s-Graduado')])),
                ('tipo_trabalho', models.SmallIntegerField(blank=True, null=True, verbose_name='Tipo de trabalho', choices=[(0, 'Carteira Assinada'), (1, 'Aut\xf4nomo'), (2, 'Servidor P\xfablico'), (3, 'Aposentado'), (4, 'Desempregado')])),
                ('qtd_estado', models.SmallIntegerField(help_text='Quantidade de anos que reside no Estado em que vive', null=True, verbose_name='Qtd. anos no Estado', blank=True)),
                ('raca', models.SmallIntegerField(blank=True, null=True, verbose_name='Ra\xe7a', choices=[(0, 'Preta'), (1, 'Parda'), (2, 'Branca'), (3, 'Amarela'), (4, 'Ind\xedgena'), (5, 'N\xe3o soube responder')])),
                ('naturalidade', models.CharField(max_length=128, null=True, blank=True)),
                ('naturalidade_estado', models.CharField(max_length=128, null=True, blank=True)),
                ('nacionalidade', models.SmallIntegerField(blank=True, null=True, verbose_name='Nacionalidade', choices=[(0, 'Brasileiro(a)'), (1, 'Brasileiro(a) Naturalizado(a)'), (2, 'Estrangeiro(a)')])),
                ('cartao_sus', models.BooleanField(verbose_name='Cart\xe3o SUS')),
                ('plano_saude', models.BooleanField(verbose_name='Plano de Sa\xfade')),
                ('foto', models.ImageField(default=None, upload_to='assistido', null=True, verbose_name='Foto', blank=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-ativo', 'nome'],
                'verbose_name': 'Assistido',
                'verbose_name_plural': 'Assistidos',
            },
            bases=('assistido.pessoa',),
        ),
        migrations.AddField(
            model_name='renda',
            name='pessoa',
            field=models.OneToOneField(to='assistido.Pessoa', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
