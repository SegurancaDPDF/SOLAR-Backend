# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cuser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistido', '0028_on_delete'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dependente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cadastrado_em', models.DateTimeField(auto_now_add=True, null=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('desativado_em', models.DateTimeField(null=True, blank=True)),
                ('nome', models.CharField(max_length=256)),
                ('parentesco', models.SmallIntegerField(verbose_name='Grau de Parentesco', choices=[(0, 'C\xf4njuge/Companheiro(a)'), (1, 'Pai/M\xe3e'), (2, 'Filho/Filha'), (3, 'Irm\xe3o/Irm\xe3'), (4, 'Tio/Tia'), (5, 'Primo/Prima'), (6, 'Av\xf3/Av\xf4'), (7, 'Outro')])),
                ('renda', models.DecimalField(default=0, help_text='Ganhos mensais, em R$, do dependente', verbose_name='Renda Individual', max_digits=16, decimal_places=2)),
                ('cadastrado_por', cuser.fields.CurrentUserField(related_name='assistido_dependente_cadastrado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('desativado_por', models.ForeignKey(related_name='assistido_dependente_desativado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', cuser.fields.CurrentUserField(related_name='assistido_dependente_modificado_por', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('pessoa', models.ForeignKey(related_name='membros', to='assistido.PessoaAssistida', on_delete=django.db.models.deletion.DO_NOTHING)),
            ],
            options={
                'ordering': ['pessoa', 'cadastrado_em'],
            },
        ),
        migrations.AddField(
            model_name='renda',
            name='previdencia',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='renda',
            name='declarante_ir',
            field=models.BooleanField(default=False, verbose_name='Declara IR?'),
        ),
        migrations.AlterField(
            model_name='renda',
            name='isento_ir',
            field=models.BooleanField(default=True, verbose_name='Isento IR?'),
        ),
    ]
