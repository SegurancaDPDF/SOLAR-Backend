# Generated by Django 3.2 on 2023-03-06 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrib', '0077_alter_defensoria_grau'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensoria',
            name='nivel_sigilo_indeferimento',
            field=models.SmallIntegerField(choices=[(0, 'Público'), (1, 'Segredo de Justiça'), (2, 'Sigilo mínimo'), (3, 'Sigilo médio'), (4, 'Sigilo intenso'), (5, 'Sigilo absoluto')], default=0, verbose_name='Nível de sigilo - Indeferimento'),
        ),
    ]
