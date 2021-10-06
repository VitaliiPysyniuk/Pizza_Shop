from django.urls import path

from .views import OrderListView, OrderRetrieveUpdateView, OrderPizzaRetrieveUpdateDeleteView, OrderCreateView, \
    StatisticView, CourierDeliveriesSortView

urlpatterns = [
    path('', OrderListView.as_view(), name='get_create_order'),
    path('/create', OrderCreateView.as_view(), name='create_new_order'),
    path('/<int:order_id>', OrderRetrieveUpdateView.as_view(), name='get_update_order'),
    path('/<int:order_id>/pizzas/<int:item_id>', OrderPizzaRetrieveUpdateDeleteView.as_view(),
         name='get_update_delete_pizza_from_order'),
    path('/statistic', StatisticView.as_view(), name='get_statistic_about_orders'),
    path('/sorted_deliveries', CourierDeliveriesSortView.as_view(), name='get_sorted_courier_deliveries')
]
