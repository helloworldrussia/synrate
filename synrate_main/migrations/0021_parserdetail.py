# Generated by Django 3.2.9 on 2022-04-04 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('synrate_main', '0020_alter_offer_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParserDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=100, null=True)),
                ('status', models.TextField(blank=True, default=None, null=True)),
                ('last_process_page', models.IntegerField(blank=True, default=1, null=True)),
            ],
        ),
    ]