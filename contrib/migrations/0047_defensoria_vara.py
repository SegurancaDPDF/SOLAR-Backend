# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contrib', '0046_defensoria_aderiu_chat_edefensor'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefensoriaVara',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('principal', models.BooleanField(default=False, help_text='\xc9 o valor default?', verbose_name='Principal')),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='contrib_defensoriavara_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('defensoria', models.ForeignKey(to='contrib.Defensoria', on_delete=django.db.models.deletion.PROTECT)),
                ('desativado_por', models.ForeignKey(related_name='contrib_defensoriavara_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='contrib_defensoriavara_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('vara', models.ForeignKey(to='contrib.Vara', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['defensoria', 'vara'],
                'db_table': 'contrib_defensoria_vara',
            },
        ),
        migrations.AddField(
            model_name='defensoria',
            name='varas',
            field=models.ManyToManyField(related_name='defensorias', through='contrib.DefensoriaVara', to='contrib.Vara'),
        ),
        migrations.AlterUniqueTogether(
            name='defensoriavara',
            unique_together=set([('defensoria', 'vara')]),
        ),
    ]
