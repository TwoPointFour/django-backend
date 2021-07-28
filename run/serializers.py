from django.db.models.fields import json
from rest_framework import serializers
from .models import Comment, ShopItem, Profile, Workout, WorkoutLog, Questionnaire, Community, Comment
from django.contrib.auth.models import User


class UserLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = "__all__"


class ProfileLiteSerializer(serializers.ModelSerializer):
    user = UserLiteSerializer()

    class Meta:
        model = Profile
        fields = ["id", "profileImage", "user", ]


class ProfileInitialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileLiteSerializer(required=False)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user)
        return user


class QuestionnaireSerializer(serializers.ModelSerializer):
    # profile = serializers.SlugRelatedField(
    # queryset=Profile.objects.all(), slug_field="user_id")

    class Meta:
        model = Questionnaire
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get('request')
        pid = request.user.profile.id
        profile = Profile.objects.get(pk=pid)
        questionnaire = Questionnaire.objects.create(
            profile=profile, **validated_data)
        return questionnaire

    # def create(self, validated_data):
    #     profile_username = validated_data.pop("profile")
    #     profile = Profile.objects.get(user__username=profile_username)
    #     questionnaire = Questionnaire.objects.create(
    #         profile=profile, **validated_data)
    #     return questionnaire


class CommunitySerializer(serializers.ModelSerializer):
    # profiles = ProfileSerializer() call a object in the class

    class Meta:
        model = Community
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    profile = ProfileLiteSerializer()

    class Meta:
        model = Comment
        fields = "__all__"


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = "__all__"


class WorkoutLogSerializer(serializers.ModelSerializer):
    profile_id = serializers.IntegerField(
        write_only=True, required=False)
    workout_id = serializers.IntegerField(
        write_only=True, required=False)
    # workouts = WorkoutSerializer(many=True)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = WorkoutLog
        fields = "__all__"

    def create(self, validated_data):
        profile_id = validated_data.pop("profile_id")
        workout_id = validated_data.pop("workout_id")
        workout = Workout.objects.get(pk=workout_id)
        profile = Profile.objects.get(pk=profile_id)
        instance = WorkoutLog.objects.create(profile=profile, **validated_data)
        instance.save()
        instance.workouts.add(workout)
        return instance


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["username", "password", "email"]

# class RegisterUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("email", "username", "password")
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         password = validated_data.pop("password", None)
#         instance = self.Meta.model(**validated_data)
#         if password is not None:
#             instance.set_password(password)
#         instance.save()
#         return instance


class ProfileSerializer(serializers.ModelSerializer):
    communities = CommunitySerializer(many=True)
    questionnaire = QuestionnaireSerializer()
    shopItems = ShopItemSerializer(many=True)
    workoutlogs = WorkoutLogSerializer(many=True)
    user = UserSerializer()
    profileImage_url = serializers.SerializerMethodField(
        "get_profileImage_url")

    class Meta:
        model = Profile
        fields = "__all__"

    def get_profileImage_url(self, obj):
        request = self.context.get('request')
        profileImage_url = obj.profileImage.url
        return request.build_absolute_uri(profileImage_url)


# class ProfileCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = "__all__"

#     def create(self, validated_data):
#         questionnaire_data = validated_data.pop("questionnaire")
#         # def super().update(self, instance, validated_data):
#         questionnaire = Questionnaire.objects.get(pk=questionnaire_data)
#         profile = Profile.objects.create(
#             questionnaire=questionnaire, **validated_data)
#         questionnaire.profile = profile
#         questionnaire.save()
#         return profile

class ProfileCreateSerializer(serializers.ModelSerializer):
    questionnaire_id = serializers.IntegerField(
        write_only=True, required=False)

    class Meta:
        model = Profile
        fields = "__all__"

    def create(self, validated_data):
        has_questionnaire_id = False
        if "questionnaire_id" in validated_data:
            has_questionnaire_id = True
            questionnaire_id = validated_data.pop("questionnaire_id")
            questionnaire = Questionnaire.objects.get(pk=questionnaire_id)
        profile = super().create(validated_data)
        if has_questionnaire_id:
            questionnaire.profile = profile
            questionnaire.save()
        return profile


class ProfileSerializerJSON(serializers.ModelSerializer):
    communities = CommunitySerializer(many=True)
    questionnaire = QuestionnaireSerializer(required=False)
    shopItems = ShopItemSerializer(many=True)
    workoutlogs = WorkoutLogSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = "__all__"

    # def create(self, validated_data):
    #     user_data = validated_data.pop("user")
    #     profile = Profile.objects.create(**validated_data)
    #     User.objects.create(profile=profile, **user_data)
    #     return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = instance.user

        # questionnaire_data = validated_data.pop("questionnaire")
        # questionnaire = instance.questionnaire
        # questionnaire.distance = questionnaire_data.get(
        # "distance", questionnaire.distance)
        # questionnaire.save()

        instance.bio = validated_data.get('bio', instance.bio)
        instance.coins += validated_data.get("coins", instance.coins)
        instance.save()

        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
        user.first_name = user_data.get('first_name', user.first_name)

        user.save()

        return instance
