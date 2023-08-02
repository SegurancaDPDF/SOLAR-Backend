# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0005_auto_20160615_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='declara_identidade_genero',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='declara_orientacao_sexual',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='nome_social',
            field=models.CharField(default=None, max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='tipo_identidade_genero',
            field=models.SmallIntegerField(default=None, null=True, verbose_name='Tipo identidade de g\xeanero', blank=True, choices=[(10, 'Travesti'), (20, 'Mulher Transexual'), (30, 'Homem Transexual'), (40, 'N\xe3o se aplica'), (50, 'Ignorado')]),
        ),
        migrations.AddField(
            model_name='pessoa',
            name='tipo_orientacao_sexual',
            field=models.SmallIntegerField(default=None, null=True, verbose_name='Tipo Orienta\xe7\xe3o sexual', blank=True, choices=[(10, 'Heterossexual'), (20, 'Homossexual'), (30, 'Bissexual')]),
        ),
    ]
