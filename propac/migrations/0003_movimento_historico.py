# Generated by Django 3.2 on 2023-02-06 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propac', '0002_tipoanexodocumentopropac_ativo'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimento',
            name='historico',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Histórico'),
        ),
    ]
