# Generated by Django 2.1.7 on 2019-11-08 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellingsapp', '0009_tarifas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarifas',
            name='canal_venta',
            field=models.CharField(choices=[('<5%', '<5%'), ('<12%', '<12%')], default='<5%', max_length=20),
        ),
    ]