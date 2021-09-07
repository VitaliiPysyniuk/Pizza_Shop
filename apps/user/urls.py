from django.urls import path

from .views import UserCreateListView, UserRetrieveUpdateView, UserFavoritesListCreateView, UserFavoriteDeleteView, \
    UserFavoritesListView, CourierDeliveriesSortView

urlpatterns = [
    path('', UserCreateListView.as_view(), name='get_all_registered_users'),
    path('/<int:pk>', UserRetrieveUpdateView.as_view(), name='get_update_user_information'),
    path('/favorites', UserFavoritesListView.as_view(), name='get_favorites_of_all_users'),
    path('/<int:user_id>/favorites', UserFavoritesListCreateView.as_view(), name='get_create_user_favorites'),
    path('/<int:user_id>/favorites/<int:pk>', UserFavoriteDeleteView.as_view(), name='delete_user_favorite'),
    path('/sorted_deliveries', CourierDeliveriesSortView.as_view(), name='get_sorted_courier_deliveries')
]
