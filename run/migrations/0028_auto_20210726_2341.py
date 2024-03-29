# Generated by Django 3.2.3 on 2021-07-26 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0027_auto_20210702_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='workoutlog',
            name='gps_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='rest_distance',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='run_distance',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workoutlog',
            name='timings',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
