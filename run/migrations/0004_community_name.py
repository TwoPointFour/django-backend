# Generated by Django 3.2.3 on 2021-06-06 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0003_auto_20210607_0427'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]