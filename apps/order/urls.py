from django.urls import path

from .views import OrderListCreateView, OrderRetrieveUpdateView, OrderPizzaRetrieveUpdateDeleteView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='list_create_order'),
    path('/<int:pk>', OrderRetrieveUpdateView.as_view(), name='get_update_order'),
    path('/pizza/<int:pk>', OrderPizzaRetrieveUpdateDeleteView.as_view(), name='get_update_delete_pizza_from_order')
]
