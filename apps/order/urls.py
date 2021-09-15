from django.urls import path

from .views import OrderListView, OrderRetrieveUpdateView, OrderPizzaRetrieveUpdateDeleteView, OrderCreateView, \
    StatisticView

urlpatterns = [
    path('', OrderCreateView.as_view(), name='create_new_order'),
    path('/list', OrderListView.as_view(), name='get_create_order'),
    path('/<int:pk>', OrderRetrieveUpdateView.as_view(), name='get_update_order'),
    path('/<int:order_id>/pizzas/<int:pk>', OrderPizzaRetrieveUpdateDeleteView.as_view(),
         name='get_update_delete_pizza_from_order'),
    path('/statistic', StatisticView.as_view(), name='get_statistic_about_orders')
]
