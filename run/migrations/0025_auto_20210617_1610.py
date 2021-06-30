# Generated by Django 3.2.3 on 2021-06-17 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0024_auto_20210613_0022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='workout',
            old_name='workout',
            new_name='workoutInfo',
        ),
        migrations.AddField(
            model_name='workout',
            name='alpha',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='workout',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='workout',
            name='variation',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='workout',
            name='week',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='workout',
            name='id',
            field=models.CharField(blank=True, max_length=50, primary_key=True, serialize=False),
        ),
    ]