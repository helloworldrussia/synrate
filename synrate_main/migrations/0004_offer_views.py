# Generated by Django 3.2.9 on 2021-11-26 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('synrate_main', '0003_auto_20211125_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='views',
            field=models.IntegerField(blank=True, default=0, verbose_name='Просмотры'),
        ),
    ]
