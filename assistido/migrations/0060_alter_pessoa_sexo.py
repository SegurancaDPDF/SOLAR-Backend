# Generated by Django 3.2 on 2023-03-30 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistido', '0059_patrimonial_assistido_patrimonial_idx_001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pessoa',
            name='sexo',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Masculino'), (1, 'Feminino'), (2, 'Desconhecido / Não informado')], default=None, null=True, verbose_name='Gênero'),
        ),
    ]