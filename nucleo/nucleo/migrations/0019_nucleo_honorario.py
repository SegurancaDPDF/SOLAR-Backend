# Generated by Django 3.2 on 2022-07-19 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0018_auto_exibir_em_gerar_alerta'),
    ]

    operations = [
        migrations.AddField(
            model_name='nucleo',
            name='honorario',
            field=models.BooleanField(default=False, help_text='Tem acesso ao módulo Honorários?'),
        ),
    ]
