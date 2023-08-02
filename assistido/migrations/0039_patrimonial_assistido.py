# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields
class Migration(migrations.Migration):

    def popular_tabela_patrimonial_tipo_com_valores_padroes(apps, schema_editor):

        Patrimonial = apps.get_model('assistido', 'Patrimonial')
        PatrimonialTipo = apps.get_model('assistido', 'PatrimonialTipo')

        PatrimonialTipo.objects.create(nome="Imóveis")
        PatrimonialTipo.objects.create(nome="Móveis")
        PatrimonialTipo.objects.create(nome="Outros Bens")
        PatrimonialTipo.objects.create(nome="Investimentos")

    def reverse_popular_tabela_patrimonial_tipo_com_valores_padroes(apps, schema_editor):
        pass

    def migracao_dados(apps, schema_editor):

        Patrimonio = apps.get_model('assistido', 'Patrimonio')
        Patrimonial = apps.get_model('assistido', 'Patrimonial')
        PatrimonialTipo = apps.get_model('assistido', 'PatrimonialTipo')

        for patrimonio in Patrimonio.objects.all():
            pessoa_id = patrimonio.pessoa_id
            if patrimonio.tem_imoveis and (patrimonio.valor_imoveis > 0):
                patrimonialTipo = PatrimonialTipo.objects.get(nome='Imóveis')
                Patrimonial.objects.create(tipo=patrimonialTipo, valor=patrimonio.valor_imoveis, pessoa_id=pessoa_id)
            if patrimonio.tem_moveis and (patrimonio.valor_moveis > 0):
                patrimonialTipo = PatrimonialTipo.objects.get(nome='Móveis')
                Patrimonial.objects.create(tipo=patrimonialTipo, valor=patrimonio.valor_moveis, pessoa_id=pessoa_id)
            if  patrimonio.tem_outros_bens and (patrimonio.valor_outros_bens > 0):
                patrimonialTipo = PatrimonialTipo.objects.get(nome='Outros Bens')
                Patrimonial.objects.create(tipo=patrimonialTipo, valor=patrimonio.valor_outros_bens, pessoa_id=pessoa_id)
            if  patrimonio.valor_investimentos and (patrimonio.valor_investimentos  > 0):
                patrimonialTipo = PatrimonialTipo.objects.get(nome='Investimentos')
                Patrimonial.objects.create(tipo=patrimonialTipo, valor=patrimonio.valor_investimentos, pessoa_id=pessoa_id)

    def reverse_migracao_dados(apps, schema_editor):
        pass

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistido', '0038_pessoaassistida_situacoes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patrimonial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('valor', models.DecimalField(default=0, max_digits=16, decimal_places=2)),
                ('descricao', models.CharField(max_length=6000, null=True, blank=True)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='assistido_patrimonial_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='assistido_patrimonial_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='assistido_patrimonial_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('pessoa', models.ForeignKey(default=None, to='assistido.Pessoa', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'verbose_name_plural': 'Patrimoniais',
            },
        ),
        migrations.CreateModel(
            name='PatrimonialTipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=256)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='assistido_patrimonialtipo_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='assistido_patrimonialtipo_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='assistido_patrimonialtipo_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='patrimonial',
            name='tipo',
            field=models.ForeignKey(default=None, to='assistido.PatrimonialTipo', on_delete=django.db.models.deletion.DO_NOTHING),
        ),
        migrations.RunPython(
            code=popular_tabela_patrimonial_tipo_com_valores_padroes,
            reverse_code=reverse_popular_tabela_patrimonial_tipo_com_valores_padroes
        ),
        migrations.RunPython(
            code=migracao_dados,
            reverse_code=reverse_migracao_dados,

        ),
    ]
