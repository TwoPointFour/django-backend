# Generated by Django 3.2.3 on 2021-06-07 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0008_user_coins'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name_plural': 'Communities'},
        ),
        migrations.AlterField(
            model_name='user',
            name='questionnaire',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='run.questionnaire'),
        ),
    ]
