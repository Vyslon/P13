# Generated by Django 2.2.4 on 2019-08-18 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_platform', '0006_auto_20190815_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade_to_rome_code',
            name='job_name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
