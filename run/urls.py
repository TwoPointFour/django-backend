from django.urls import path
from . import views
from rest_framework.authtoken import views as authviews
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)


urlpatterns = [
    path("predict/", views.Predict().as_view()),
    path("suggest/", views.Suggest().as_view()),
    path("profiles/", views.ProfileList.as_view()),
    path("profile/new/", views.ProfileCreate.as_view()),
    path("profile/create/", views.UserProfileCreate.as_view()),
    path("profile/dp/", views.ProfileUpdateForm.as_view()),
    path("profile/initialize", views.ProfileInitialize.as_view()),
    path("profile/<int:pk>/", views.ProfileDetail.as_view()),
    path("user/", views.UserView.as_view()),
    path("user/update/", views.UserUpdate.as_view()),
    path("profile/update/", views.ProfileUpdate.as_view()),
    path("questionnaire/create/", views.QuestionnaireCreate.as_view()),
    # path('login/', views.CustomAuthToken.as_view()),
    # path('signup/', views.SignUpUser.as_view()),
    # path('login/', authviews.obtain_auth_token),
    path("register/", views.UserCreateView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name='token_obtain_par'),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/blacklist/", views.BlacklistTokenView.as_view(), name="blacklist")
]

urlpatterns = format_suffix_patterns(urlpatterns)
