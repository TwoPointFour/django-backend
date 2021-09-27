from django.contrib import admin
from django.db import models
from .models import Questionnaire, Workout, Profile, WorkoutLog, Community, Comment, ShopItem
# from .models import Workout, User

# Register your models here.

# admin.site.register(Workout)
# admin.site.register(User)


class CommunityMembershipInline(admin.TabularInline):
    model = Profile.communities.through


class ProfileWorkoutInline(admin.TabularInline):
    model = WorkoutLog


class WorkoutLogCommentInline(admin.TabularInline):
    model = Comment


class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("id", "alpha", "type", "measurement",
                    "difficultyMultiplier", "workoutInfo")


# class QuestionnaireProfileInline(admin.TabularInline):
#     model = Profile


class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProfileWorkoutInline, WorkoutLogCommentInline]


class WorkoutLogAdmin(admin.ModelAdmin):
    inlines = [WorkoutLogCommentInline]


class QuestionnaireAdmin(admin.ModelAdmin):
    # inlines = [QuestionnaireProfileInline]
    list_display = ("profile", "distance", "duration", "experience", "frequency",
                    "latest", "target", "workoutFrequency", "regular")


class CommunityAdmin(admin.ModelAdmin):
    # list_display = ("name", "users", "workouts")
    inlines = [CommunityMembershipInline]


admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(Workout, WorkoutAdmin)
admin.site.register(Comment)
admin.site.register(ShopItem)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(WorkoutLog, WorkoutLogAdmin)
admin.site.register(Community, CommunityAdmin)
