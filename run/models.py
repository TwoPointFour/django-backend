from django.db import models
from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField, FloatField
from django.db.models.fields.json import JSONField
from django.contrib.auth.models import User

# Create your models here.


# class User(models.Model):
#     displayName = models.CharField(max_length=50)
#     bio = models.CharField(max_length=300)
#     email = models.EmailField(max_length=200)
#     currentFitness = models.FloatField(null=True)


# class Workout(models.Model):
#     difficultyMultiplier = models.FloatField(null=True)
#     parts = models.JSONField(blank=True)


# class Training(models.Model):
#     workout = models.ForeignKey(
#         Workout, on_delete=models.SET_NULL, related_name="training", null=True)
#     profile = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="profile", null=True)
#     date = models.DateTimeField(auto_now=True)
#     timings = models.JSONField(blank=True)

############################################################

def upload_to(instance, filename):
    return 'run/{filename}'.format(filename=filename)


class Questionnaire(models.Model):
    distance = models.FloatField(null=True)
    duration = models.IntegerField(null=True)
    experience = models.IntegerField(null=True)
    frequency = models.IntegerField(null=True)
    latest = models.DurationField()
    target = models.DurationField()
    workoutFrequency = models.IntegerField(null=True)
    regular = models.BooleanField(null=True)
    profile = models.OneToOneField(
        "Profile", on_delete=models.SET_NULL, null=True, related_name="questionnaire", blank=True)

    def __str__(self):
        try:
            return f"{self.profile}"
        except:
            return "No User Assigned"


class Workout(models.Model):
    workoutInfo = models.JSONField(blank=True, null=True, default=dict)
    id = models.CharField(primary_key=True, max_length=50)
    alpha = models.FloatField(null=True, blank=True)
    difficultyMultiplier = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.workoutInfo}"


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="profile")
    bio = models.CharField(max_length=300, blank=True)
    alias = models.CharField(max_length=50, blank=True)
    currentFitness = models.FloatField(null=True)
    profileImage = models.ImageField(
        upload_to=upload_to, default="default/default.jpg")
    # questionnaire = models.OneToOneField(
    #     Questionnaire, on_delete=models.SET_NULL, null=True, related_name="profile", blank=True)
    communities = models.ManyToManyField(
        "Community", related_name="profiles", blank=True)
    friends = models.ManyToManyField("self", blank=True)
    shopItems = models.ManyToManyField(
        "ShopItem", related_name="profiles", blank=True)
    coins = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user}"


class WorkoutLog(models.Model):
    workouts = models.ManyToManyField(
        Workout, blank=True, related_name="workoutlogs")
    timings = models.JSONField(blank=True)
    datetime = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="workoutlogs", related_query_name="workoutlogs", null=True)

    class Meta:
        ordering = ["-datetime"]

    def __str__(self):
        return f"{self.profile} {self.datetime}"


class Community(models.Model):
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Communities"


class Comment(models.Model):
    content = models.CharField(max_length=200)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name="comments")
    workoutLog = models.ForeignKey(
        WorkoutLog, on_delete=models.CASCADE, blank=True, null=True, related_name="comments")


class ShopItem(models.Model):
    name = CharField(max_length=100, blank=True)
    description = CharField(max_length=100, blank=True)
    price = FloatField(null=True)
    type = CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name}"


data = [{"distance": 300, "restMultiplier": 2, "sets": 10},
        {"distance": 400, "restMultiplier": 2.33, "sets": 8},
        {"distance": 500, "restMultiplier": 2.6, "sets": 6},
        {"distance": 600, "restMultiplier": 2.8, "sets": 5},
        {"distance": 700, "restMultiplier": 3.2, "sets": 4},
        {"distance": 800, "restMultiplier": 4, "sets": 4},
        {"distance": 1000, "restMultiplier": 4.5, "sets": 3},
        {"distance": 300, "restMultiplier": 2, "sets": 8},
        {"distance": 300, "restMultiplier": 2, "sets": 9},
        {"distance": 400, "restMultiplier": 2.33, "sets": 6},
        {"distance": 400, "restMultiplier": 2.33, "sets": 7},
        {"distance": 500, "restMultiplier": 2.6, "sets": 5},
        {"distance": 600, "restMultiplier": 2.8, "sets": 4},
        {"distance": 700, "restMultiplier": 3.2, "sets": 3},
        {"distance": 800, "restMultiplier": 4, "sets": 3},
        {"distance": 900, "restMultiplier": 4.25, "sets": 3},
        {"distance": 1100, "restMultiplier": 4.5, "sets": 2},
        {"distance": 1100, "restMultiplier": 4.75, "sets": 2},
        {"distance": 1200, "restMultiplier": 5, "sets": 2},
        {"distance": 800, "restMultiplier": 4, "sets": 3},
        {"distance": 400, "restMultiplier": 0, "sets": 1},
        {"distance": 800, "restMultiplier": 4, "sets": 3},
        {"distance": 500, "restMultiplier": 0, "sets": 1},
        {"distance": 800, "restMultiplier": 4, "sets": 3},
        {"distance": 600, "restMultiplier": 0, "sets": 1},
        {"distance": 1000, "restMultiplier": 4.5, "sets": 2},
        {"distance": 400, "restMultiplier": 0, "sets": 1},
        {"distance": 1000, "restMultiplier": 4.5, "sets": 2},
        {"distance": 500, "restMultiplier": 0, "sets": 1},
        {"distance": 1000, "restMultiplier": 4.5, "sets": 2},
        {"distance": 600, "restMultiplier": 0, "sets": 1},
        {"distance": 1000, "restMultiplier": 4.5, "sets": 2},
        {"distance": 700, "restMultiplier": 0, "sets": 1},
        {"distance": 1000, "restMultiplier": 4.5, "sets": 2},
        {"distance": 800, "restMultiplier": 0, "sets": 1},
        {"distance": 1200, "restMultiplier": 5, "sets": 2},
        {"distance": 400, "restMultiplier": 0, "sets": 1},
        {"distance": 1200, "restMultiplier": 5, "sets": 2},
        {"distance": 500, "restMultiplier": 0, "sets": 1},
        {"distance": 1200, "restMultiplier": 5, "sets": 1},
        {"distance": 800, "restMultiplier": 4, "sets": 1},
        {"distance": 400, "restMultiplier": 0, "sets": 1},
        {"distance": 1200, "restMultiplier": 5, "sets": 1},
        {"distance": 800, "restMultiplier": 4, "sets": 1},
        {"distance": 600, "restMultiplier": 0, "sets": 1},
        {"distance": 400, "restMultiplier": 2, "sets": 1},
        {"distance": 800, "restMultiplier": 4, "sets": 2},
        {"distance": 400, "restMultiplier": 0, "sets": 1},
        ]
