# Generated by Django 3.2 on 2022-08-04 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0117_tarefa_movimento'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualificacao',
            name='numero',
            field=models.SmallIntegerField(default=0),
        ),
    ]
