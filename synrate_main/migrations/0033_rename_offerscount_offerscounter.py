# Generated by Django 3.2.9 on 2022-05-18 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('synrate_main', '0032_offerscount_home_lilter'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OffersCount',
            new_name='OffersCounter',
        ),
    ]