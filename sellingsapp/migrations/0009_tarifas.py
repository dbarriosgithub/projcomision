# Generated by Django 2.1.7 on 2019-10-31 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellingsapp', '0008_auto_20191024_1707'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tarifas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limite_inf', models.IntegerField(default=0)),
                ('limite_sup', models.IntegerField(default=0)),
                ('nombre_rango', models.CharField(choices=[('R1', 'R1'), ('R2', 'R2'), ('R3', 'R3'), ('R4', 'R4'), ('R5', 'R5'), ('R6', 'R6')], default='R1', max_length=20)),
                ('porce_title', models.CharField(max_length=200)),
                ('canal_venta', models.CharField(choices=[('FVD', 'FVD'), ('CU', 'CU')], default='FVD', max_length=20)),
                ('comision', models.IntegerField(default=0)),
            ],
        ),
    ]
