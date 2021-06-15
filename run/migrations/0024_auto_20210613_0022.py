# Generated by Django 3.2.3 on 2021-06-12 16:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0023_auto_20210612_0126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='questionnaire',
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='profile',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questionnaire', to='run.profile'),
        ),
    ]