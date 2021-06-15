# Generated by Django 3.2.3 on 2021-06-08 17:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('run', '0012_alter_user_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayName', models.CharField(max_length=50)),
                ('bio', models.CharField(max_length=300)),
                ('email', models.EmailField(max_length=200)),
                ('currentFitness', models.FloatField(null=True)),
                ('profileImage', models.ImageField(blank=True, null=True, upload_to='images')),
                ('coins', models.IntegerField(default=0)),
                ('communities', models.ManyToManyField(blank=True, related_name='profiles', to='run.Community')),
                ('friends', models.ManyToManyField(blank=True, related_name='_run_profile_friends_+', to='run.Profile')),
                ('questionnaire', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profile', to='run.questionnaire')),
                ('shopItems', models.ManyToManyField(blank=True, related_name='profiles', to='run.ShopItem')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='workoutlog',
            name='user',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='comment',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='run.profile'),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='workoutlogs', to='run.profile'),
        ),
    ]