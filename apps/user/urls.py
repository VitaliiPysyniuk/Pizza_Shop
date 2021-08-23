from django.urls import path

from .views import UserCreateListView, CourierUpdateView

urlpatterns = [
    path('', UserCreateListView.as_view(), name='list_all_users'),
    path('/<int:pk>/update', CourierUpdateView.as_view(), name='update_courier_info')
]
