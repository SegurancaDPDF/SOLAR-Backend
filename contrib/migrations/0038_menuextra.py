# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0037_defensoria_pode_vincular_tarefa_de_cooperacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuExtra',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('local', models.CharField(default='ajuda', max_length=255, choices=[('root', 'Root'), ('ajuda', 'Ajuda')])),
                ('posicao', models.PositiveSmallIntegerField()),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('icone', models.CharField(max_length=255)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='contrib_menuextra_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='contrib_menuextra_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='contrib_menuextra_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['local', 'posicao'],
                'verbose_name': 'Menu Extra',
                'verbose_name_plural': 'Menus Extra',
            },
        ),
    ]
