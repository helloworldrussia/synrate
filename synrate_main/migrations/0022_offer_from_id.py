# Generated by Django 3.2.9 on 2022-04-06 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('synrate_main', '0021_parserdetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='from_id',
            field=models.TextField(blank=True, default='', null=True, verbose_name='ID от источника'),
        ),
    ]