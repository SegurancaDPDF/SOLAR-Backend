# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('contrib', '0012_defensoria_categorias_de_agendas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Papel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=256)),
                ('requer_supervisor', models.BooleanField(default=False, help_text='Necess\xe1rio possuir defensor supervisor para utilizar esse papel')),
                ('requer_matricula', models.BooleanField(default=True, help_text='Necess\xe1rio possuiu numero de matricula para utilizar esse papel')),
                ('requer_superusuario', models.BooleanField(default=False, help_text='Utilizado para filtrar papeis dos administradores do sistema')),
                ('ativo', models.BooleanField(default=True)),
                ('grupos', models.ManyToManyField(to='auth.Group')),
            ],
            options={
                'verbose_name': 'Papel',
                'verbose_name_plural': 'Pap\xe9is',
            },
        ),
        migrations.AlterField(
            model_name='servidor',
            name='matricula',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AddField(
            model_name='servidor',
            name='papel',
            field=models.ForeignKey(related_name='servidores', to='contrib.Papel', help_text='Conjunto de Permisss\xf5es do usu\xe1rio', null=True, on_delete=django.db.models.deletion.DO_NOTHING),
        ),
    ]
