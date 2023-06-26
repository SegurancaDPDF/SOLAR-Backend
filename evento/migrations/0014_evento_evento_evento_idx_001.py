# Generated by Django 3.2 on 2023-02-14 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evento', '0013_categoria_eh_categoria_crc'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='evento',
            index=models.Index(fields=['tipo', 'data_validade', 'data_fim'], name='evento_evento_idx_001'),
        ),
    ]