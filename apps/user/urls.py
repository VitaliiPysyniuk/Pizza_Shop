from django.urls import path

from .views import UserCreateListView, CourierUpdateView, UserFavoritesListCreateView, UserFavoriteDeleteView

urlpatterns = [
    path('', UserCreateListView.as_view(), name='list_all_users'),
    path('/<int:pk>/update', CourierUpdateView.as_view(), name='update_courier_info'),
    path('/favorite', UserFavoritesListCreateView.as_view(), name='list_create_user_favorite'),
    path('/favorite/<int:pk>', UserFavoriteDeleteView.as_view(), name='delete_user_favorite')
]
