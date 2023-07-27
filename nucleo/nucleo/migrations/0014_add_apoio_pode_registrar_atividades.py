# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_data(apps, schema_editor):
    Nucleo = apps.get_model("nucleo", "Nucleo")

    # Habilita recurso para registrar atividades em apoios da multidisciplinar
    Nucleo.objects.filter(multidisciplinar=True).update(apoio_pode_registrar_atividades=True)


def reverse_migrate_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0013_nucleo_livre'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='apoio_pode_registrar_atividades',
            field=models.BooleanField(default=False, verbose_name='Pode registrar atividades em pedidos de apoio?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='acordo',
            field=models.BooleanField(default=False, help_text='Aceita registrar atendimentos de acordo?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='agendamento',
            field=models.BooleanField(default=False, help_text='Aceita receber agendamentos (inicial/retorno)?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='apoio',
            field=models.BooleanField(default=True, help_text='Aceita receber pedidos de apoio?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='coletivo',
            field=models.BooleanField(default=False, help_text='Aceita registrar atendimentos coletivos?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='diligencia',
            field=models.BooleanField(default=False, help_text='\xc9 um n\xfacleo de Dilig\xeancias?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='encaminhamento',
            field=models.BooleanField(default=True, help_text='Aceita receber agendamentos via encaminhamento?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='itinerante',
            field=models.BooleanField(default=False, help_text='\xc9 um n\xfacleo Itinerante/Multir\xe3o?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='livre',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo Livre?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='multidisciplinar',
            field=models.BooleanField(default=False, help_text='\xc9 um n\xfacleo Multidisciplinar?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='plantao',
            field=models.BooleanField(default=False, help_text='\xc9 um n\xfacleo de Plant\xe3o?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='propac',
            field=models.BooleanField(default=False, help_text='Tem acesso ao m\xf3dulo Propacs?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='recursal',
            field=models.BooleanField(default=False, help_text='\xc9 um n\xfacleo Recursal?'),
        ),
        migrations.AlterField(
            model_name='nucleo',
            name='supervisionado',
            field=models.BooleanField(default=False, help_text='Os assessores/estagi\xe1rios s\xf3 ver\xe3o os atendimentos a que lhe forem distribu\xeddos'),
        ),
        migrations.RunPython(
            code=migrate_data,
            reverse_code=reverse_migrate_data,
            atomic=True
        ),
    ]
