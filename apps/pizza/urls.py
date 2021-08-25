from django.urls import path

from .views import PizzaListView, PizzaCreateView, PizzaSizeCreateView, PizzaUpdateDeleteView, PizzaSizeUpdateDeleteView

urlpatterns = [
    path('', PizzaListView.as_view(), name='get_all_pizzas'),
    path('/create', PizzaCreateView.as_view(), name='create_pizza'),
    path('/<int:pk>', PizzaUpdateDeleteView.as_view(), name='get_update_delete_pizza'),
    path('/<int:pizza_id>/sizes', PizzaSizeCreateView.as_view(), name='add_pizza_size'),
    path('/<int:pizza_id>/sizes/<int:pk>', PizzaSizeUpdateDeleteView.as_view(), name='get_update_delete_pizza_size')
]
