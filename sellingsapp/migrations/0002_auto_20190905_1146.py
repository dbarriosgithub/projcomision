# Generated by Django 2.1.7 on 2019-09-05 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sellingsapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='solicitud',
            old_name='num_campaign',
            new_name='product_cant',
        ),
        migrations.AddField(
            model_name='solicitud',
            name='dia',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='solicitud',
            name='product_name',
            field=models.CharField(choices=[('On', 'One play'), ('Dp', 'Duo play'), ('Tp', 'Triple play')], default='One play', max_length=6),
        ),
    ]
