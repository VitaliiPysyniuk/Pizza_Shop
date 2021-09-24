from django.urls import path

from .views import UserRegisterView, UserActivateView, TokenObtainPairViewCustom, TokenRefreshViewCustom

urlpatterns = [
    path('', TokenObtainPairViewCustom.as_view(), name='obtain_token_pair'),
    path('/refresh', TokenRefreshViewCustom.as_view(), name='refresh_access_token'),
    path('/register', UserRegisterView.as_view(), name='register_new_user'),
    path('/activate', UserActivateView.as_view(), name='activate_new_user')
]
