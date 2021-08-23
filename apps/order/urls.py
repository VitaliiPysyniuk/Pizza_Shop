from django.urls import path

from .views import OrderListCreateView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='list_create_order')
]
