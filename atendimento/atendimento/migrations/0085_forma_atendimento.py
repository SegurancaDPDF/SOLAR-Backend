# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields
from datetime import datetime


def migrate_data(apps, schema_editor):
    FormaAtendimento = apps.get_model("atendimento", "FormaAtendimento")

    FormaAtendimento.objects.create(
        nome='Presencial',
        presencial=True,
        data_inicial=datetime.now()
    )


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('atendimento', '0084_viewatendimentodefensor'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormaAtendimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=512, db_index=True)),
                ('data_inicial', models.DateTimeField(verbose_name='Data inicial')),
                ('data_final', models.DateTimeField(default=None, null=True, verbose_name='Data final', blank=True)),
                ('conta_estatistica', models.BooleanField(default=True, help_text='Conta Estat\xedstica?', verbose_name='Conta estat\xedsticas')),
                ('aparece_defensor', models.BooleanField(default=True, help_text='Aparece para o defensor?', verbose_name='Aparece para o defensor?')),
                ('aparece_recepcao', models.BooleanField(default=True, help_text='Aparece para a recep\xe7\xe3o?', verbose_name='Aparece para a recep\xe7\xe3o?')),
                ('por_email', models.BooleanField(default=False, help_text='O atendimento foi por e-mail?', verbose_name='Atendido por e-mail?')),
                ('por_app_mensagem', models.BooleanField(default=False, help_text='O atendimento foi por WhatsApp/Telegram?', verbose_name='Atendido por mensagem?')),
                ('por_ligacao', models.BooleanField(default=False, help_text='O atendimento foi por liga\xe7\xe3o?', verbose_name='Atendido por liga\xe7\xe3o?')),
                ('presencial', models.BooleanField(default=False, help_text='O atendimento foi presencial?', verbose_name='Atendido presencialmente?')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='atendimento_formaatendimento_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='atendimento_formaatendimento_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='atendimento_formaatendimento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'atendimento_forma_atendimento',
                'verbose_name': 'Forma de atendimento',
                'verbose_name_plural': 'Formas de atendimento',
            },
        ),
        migrations.AddField(
            model_name='atendimento',
            name='forma_atendimento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='atendimento.FormaAtendimento', null=True, verbose_name='Forma de atendimento'),
        ),
        migrations.AlterUniqueTogether(
            name='formaatendimento',
            unique_together=set([('nome', 'data_inicial', 'data_final')]),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
