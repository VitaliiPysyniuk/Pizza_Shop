from django.urls import path

from .views import PizzaListView, PizzaCreateView, PizzaSizeCreateView, PizzaUpdateDeleteView, PizzaSizeUpdateDeleteView

urlpatterns = [
    path('', PizzaListView.as_view(), name='get_all_pizzas'),
    path('/create', PizzaCreateView.as_view(), name='get_create_pizza_with_size'),
    path('/<int:pk>', PizzaUpdateDeleteView.as_view(), name='update_delete_pizza'),
    path('/<int:pk>/add_size', PizzaSizeCreateView.as_view(), name='add_pizza_size'),
    path('/<int:pk>/size', PizzaSizeUpdateDeleteView.as_view(), name='update_delete_pizza_size')
]
