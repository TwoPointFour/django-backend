# Generated by Django 3.2.3 on 2021-06-07 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0007_auto_20210607_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='coins',
            field=models.IntegerField(default=0),
        ),
    ]