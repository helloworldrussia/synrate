# Generated by Django 3.2.9 on 2022-03-31 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('synrate_main', '0018_alter_offer_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=1500, null=True, verbose_name='Название'),
        ),
    ]