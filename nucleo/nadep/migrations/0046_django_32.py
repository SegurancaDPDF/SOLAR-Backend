# Generated by Django 3.2 on 2021-05-24 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atendimento', '0103_django_32'),
        ('nadep', '0045_prisao_resultado_sentenca_abs_imp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='defensor_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='atendimento.defensor'),
        ),
    ]
