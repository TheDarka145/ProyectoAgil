# Generated by Django 5.0.6 on 2024-06-26 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planta',
            name='precio',
            field=models.IntegerField(verbose_name='Precio de la Planta'),
        ),
    ]
