# Generated by Django 3.2.9 on 2022-05-12 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('synrate_main', '0027_auto_20220420_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='slug',
            field=models.CharField(blank=True, db_index=True, default=None, max_length=255, null=True, verbose_name='ЧПУ'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='url',
            field=models.CharField(blank=True, default=None, max_length=599, null=True, verbose_name='Ссылка на источник'),
        ),
    ]
