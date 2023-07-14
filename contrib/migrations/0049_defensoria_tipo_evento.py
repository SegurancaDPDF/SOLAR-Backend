# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_classe_indeferimento_pode_registrar_recurso'),
        ('contrib', '0048_defensoriavara_paridade'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefensoriaTipoEvento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('conta_estatistica', models.BooleanField(default=True, help_text='Conta Estat\xedsticas?')),
                ('defensoria', models.ForeignKey(to='contrib.Defensoria', on_delete=django.db.models.deletion.PROTECT)),
                ('tipo_evento', models.ForeignKey(to='core.TipoEvento', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ['defensoria', 'tipo_evento'],
                'db_table': 'contrib_defensoria_tipos_eventos',
                'verbose_name': 'Defensoria / Tipos de Evento',
                'verbose_name_plural': 'Defensorias / Tipos de Evento'
            },
        ),
        migrations.AddField(
            model_name='defensoria',
            name='tipos_eventos',
            field=models.ManyToManyField(related_name='defensorias', through='contrib.DefensoriaTipoEvento', to='core.TipoEvento'),
        ),
        migrations.AlterUniqueTogether(
            name='defensoriatipoevento',
            unique_together=set([('defensoria', 'tipo_evento')]),
        ),
        migrations.AlterModelTable(
            name='defensoriavara',
            table='contrib_defensoria_varas',
        ),
        migrations.AlterModelOptions(
            name='defensoriavara',
            options={'ordering': ['defensoria', 'vara'], 'verbose_name': 'Defensoria / Vara', 'verbose_name_plural': 'Defensorias / Varas'},
        ),
    ]
