# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0032_defensoria_pode_vincular_processo_judicial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnderecoHistorico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logradouro', models.CharField(default=None, max_length=256, null=True, blank=True)),
                ('numero', models.CharField(default=None, max_length=32, null=True, verbose_name='N\xfamero', blank=True)),
                ('complemento', models.CharField(default=None, max_length=512, null=True, verbose_name='Complemento', blank=True)),
                ('cep', models.CharField(default=None, max_length=32, null=True, verbose_name='CEP', blank=True)),
                ('tipo_area', models.SmallIntegerField(default=None, null=True, blank=True, choices=[(0, 'Urbana'), (1, 'Rural')])),
                ('principal', models.BooleanField(default=False, verbose_name='Principal')),
                ('tipo', models.SmallIntegerField(default=None, null=True, blank=True, choices=[(10, 'Residencial'), (20, 'Comercial'), (30, 'Correspond\xeancia'), (40, 'Alternativo')])),
                ('cadastrado_em', models.DateTimeField(null=True)),
                ('modificado_em', models.DateTimeField(null=True)),
                ('desativado_em', models.DateTimeField(null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='endereco',
            options={'ordering': ['-principal', 'logradouro'], 'verbose_name': 'Endere\xe7o', 'verbose_name_plural': 'Endere\xe7os'},
        ),
        migrations.AddField(
            model_name='endereco',
            name='cadastrado_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='endereco',
            name='cadastrado_por',
            field=cuser.fields.CurrentUserField(related_name='contrib_endereco_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='endereco',
            name='desativado_em',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='endereco',
            name='desativado_por',
            field=models.ForeignKey(related_name='contrib_endereco_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='endereco',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='endereco',
            name='modificado_por',
            field=cuser.fields.CurrentUserField(related_name='contrib_endereco_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='endereco',
            name='principal',
            field=models.BooleanField(default=False, verbose_name='Principal'),
        ),
        migrations.AddField(
            model_name='endereco',
            name='tipo',
            field=models.SmallIntegerField(default=10, blank=True, choices=[(10, 'Residencial'), (20, 'Comercial'), (30, 'Correspond\xeancia'), (40, 'Alternativo')]),
        ),
        migrations.AlterField(
            model_name='bairro',
            name='municipio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='contrib.Municipio', null=True),
        ),
        migrations.AlterField(
            model_name='cep',
            name='municipio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='contrib.Municipio', null=True),
        ),
        migrations.AlterField(
            model_name='comarca',
            name='coordenadoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='contrib.Comarca', null=True),
        ),
        migrations.AlterField(
            model_name='defensoria',
            name='comarca',
            field=models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='defensoria',
            name='nucleo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='nucleo.Nucleo', null=True),
        ),
        migrations.AlterField(
            model_name='defensoria',
            name='predio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='comarca.Predio', null=True),
        ),
        migrations.AlterField(
            model_name='endereco',
            name='bairro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='contrib.Bairro', null=True),
        ),
        migrations.AlterField(
            model_name='endereco',
            name='municipio',
            field=models.ForeignKey(to='contrib.Municipio', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='comarca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='contrib.Comarca', null=True),
        ),
        migrations.AlterField(
            model_name='municipio',
            name='estado',
            field=models.ForeignKey(to='contrib.Estado', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='comarca',
            field=models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='servidor',
            name='papel',
            field=models.ForeignKey(related_name='servidores', on_delete=django.db.models.deletion.PROTECT, to='contrib.Papel', help_text='Conjunto de Permisss\xf5es do usu\xe1rio', null=True),
        ),
        migrations.AlterField(
            model_name='vara',
            name='comarca',
            field=models.ForeignKey(to='contrib.Comarca', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='enderecohistorico',
            name='bairro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='contrib.Bairro', null=True),
        ),
        migrations.AddField(
            model_name='enderecohistorico',
            name='cadastrado_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='enderecohistorico',
            name='desativado_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='enderecohistorico',
            name='endereco',
            field=models.ForeignKey(related_name='historicos', on_delete=django.db.models.deletion.PROTECT, to='contrib.Endereco'),
        ),
        migrations.AddField(
            model_name='enderecohistorico',
            name='modificado_por',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='enderecohistorico',
            name='municipio',
            field=models.ForeignKey(to='contrib.Municipio', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
