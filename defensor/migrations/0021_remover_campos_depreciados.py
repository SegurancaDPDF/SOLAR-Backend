# Generated by Django 3.2 on 2022-07-05 16:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defensor', '0020_defensor_data_expiracao_credenciais_mni'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='defensor',
            name='nao_possui_eproc',
        ),
        migrations.RemoveField(
            model_name='defensor',
            name='senha_eproc',
        ),
    ]
