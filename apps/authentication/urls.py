from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterUserView

urlpatterns = [
    path('', TokenObtainPairView.as_view(), name='obtain_token_pair'),
    path('/refresh', TokenRefreshView.as_view(), name='refresh_access_token'),
    path('/register', RegisterUserView.as_view(), name='register_new_user')
]
