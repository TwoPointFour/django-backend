# Generated by Django 3.2.3 on 2021-06-06 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('run', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField(null=True)),
                ('duration', models.IntegerField(null=True)),
                ('experience', models.IntegerField(null=True)),
                ('frequency', models.IntegerField(null=True)),
                ('latest', models.DurationField()),
                ('target', models.DurationField()),
                ('workoutFrequency', models.IntegerField(null=True)),
                ('regular', models.BooleanField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timings', models.JSONField(blank=True)),
                ('datetime', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='workout',
            name='difficultyMultiplier',
        ),
        migrations.RemoveField(
            model_name='workout',
            name='parts',
        ),
        migrations.AddField(
            model_name='user',
            name='friends',
            field=models.ManyToManyField(null=True, related_name='_run_user_friends_+', to='run.User'),
        ),
        migrations.AddField(
            model_name='user',
            name='profileImage',
            field=models.ImageField(null=True, upload_to='images'),
        ),
        migrations.AddField(
            model_name='workout',
            name='workout',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Training',
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='workoutlogs', to='run.user'),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='workout',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='run.workout'),
        ),
        migrations.AddField(
            model_name='community',
            name='workouts',
            field=models.ManyToManyField(null=True, related_name='communities', to='run.WorkoutLog'),
        ),
        migrations.AddField(
            model_name='user',
            name='communities',
            field=models.ManyToManyField(null=True, related_name='users', to='run.Community'),
        ),
        migrations.AddField(
            model_name='user',
            name='questionnaire',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='run.questionnaire'),
        ),
    ]
