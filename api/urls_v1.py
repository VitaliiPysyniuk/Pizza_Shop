from django.urls import path, include

urlpatterns = [
    path('/auth', include('apps.authentication.urls'), name='auth_api'),
    path('/pizza', include('apps.pizza.urls'), name='pizza_api'),
    path('/order', include('apps.order.urls'), name='order_api'),
    path('/user', include('apps.user.urls'), name='user_api')
]

