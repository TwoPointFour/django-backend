# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from .models import Profile, Questionnaire
from .serializers import ProfileInitialSerializer, ProfileSerializer, UserSerializer, ProfileSerializerJSON, QuestionnaireSerializer, ProfileCreateSerializer
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework import serializers, status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
#
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from run.algorithms.suggest import get_training_plan
from run.algorithms.suggest import get_predicted_time

# Create your views here.


# @csrf_exempt
# class UserList(APIView):
#     def get(self, request, format=None):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileEditPermission(BasePermission):
    message = "You do not have edit the details of this user"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class QuestionnaireCreate(generics.CreateAPIView):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = QuestionnaireSerializer(data=request.data, context={
                                             "request": request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserUpdate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    serializer_class = UserSerializer


class ProfileCreate(generics.CreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileCreateSerializer
    permission_classes = [IsAuthenticated]


class ProfileUpdate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        serializer = ProfileSerializerJSON(
            request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileCreate(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = ProfileSerializer(
            request.user.profile, context={'request': request}, data=request.data, partial=True)
        if serializer.is_valid():
            print(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateForm(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = ProfileSerializer(
            request.user.profile, context={'request': request}, data=request.data, partial=True)
        if serializer.is_valid():
            print(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView, ProfileEditPermission):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, ProfileEditPermission]


class ProfileInitialize(APIView):
    def get_object(self, request):
        try:
            return request.user.profile
        except:
            raise Http404

    def get(self, request, format=None):
        profile = self.get_object(request)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)


# class SignUpUser(APIView):
#     parser_classes = [JSONParser]

#     def post(self, request, format=None):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = User.objects.create_user(
#                 serializer.data.username, serializer.data.email, serializer.data.password)
#             return Response({
#                 "username": serializer.data.username,
#                 "email": serializer.data.email
#             })
#         else:
#             return Response(serializer.errors)

# class CustomUserCreate(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         reg_serializer = RegisterUserSerializer(data=request.data)
#         if reg_serializer.is_valid():
#             newuser = reg_serializer.save()
#             if newuser:
#                 return Response(status=status.HTTP_201_CREATED)
#         return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class Suggest(generics.RetrieveAPIView):
    def get(self, request, **kwargs):
        var = get_training_plan()
        return Response({
            "Training Plan": var
        })

class Predict(generics.RetrieveAPIView):
    def get(self, request, **kwargs):
        var = get_predicted_time()
        return Response({
            "Training Plan": var
        })

from .forms import TestAlgorithm

def test_algorithm(request):
    if request.method == 'POST':
        pass
        # form = TestAlgorithm(request.POST)
        # return Response({
        #         "Training Plan": 'var'
        # })
    else:
        # proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = TestAlgorithm(initial={})

    context = {
        'form': form
    }

    return render(request, 'test.html', context)

# # @csrf_exempt
# class UserDetail(APIView):
#     def get_object(self, pk):
#         try:
#             return User.objects.get(pk=pk)
#         except User.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         user = self.get_object(pk)
#         serializer = UserSerializer(user)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         user = self.get_object(pk)
#         serializer = UserSerializer(user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         user = self.get_object(pk)
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @csrf_exempt
# @api_view(["GET", "POST"])
# def user_detail(request, pk, format=None):
#     """
#     Retrieve, update or delete a code user.
#     """
#     try:
#         user = User.objects.get(pk=pk)
#     except User.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = UserSerializer(user)
#         return Response(serializer.data)

#     elif request.method == 'PUT':
#         serializer = UserSerializer(user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':
#         user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# @csrf_exempt
# @api_view(["GET", "POST"])
# def user_list(request, format=None):
#     if request.method == "GET":
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)