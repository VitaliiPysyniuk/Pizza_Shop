from django.urls import path

from .views import OrderListCreateView, OrderRetrieveUpdateView, OrderPizzaRetrieveUpdateDeleteView, OrderCreateView

urlpatterns = [
    path('/create', OrderCreateView.as_view(), name='create_new_order'),
    path('', OrderListCreateView.as_view(), name='get_create_order'),
    path('/<int:pk>', OrderRetrieveUpdateView.as_view(), name='get_update_order'),
    path('/<int:order_id>/pizzas/<int:pk>', OrderPizzaRetrieveUpdateDeleteView.as_view(),
         name='get_update_delete_pizza_from_order')
]
