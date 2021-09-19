from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view, renderers
from rest_framework.schemas import get_schema_view, openapi

schema_view = get_swagger_view(title='PizzaShop API', )
# schema_view = get_schema_view(title='PizzaShop API', description='API documentation for PizzaShop.', version="1.0.0",
#                               public=True)
                              # renderer_classes=[renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])

urlpatterns = [
    path('/auth', include('apps.authentication.urls'), name='auth_api'),
    path('/user', include('apps.user.urls'), name='user_api'),
    path('/pizza', include('apps.pizza.urls'), name='pizza_api'),
    path('/order', include('apps.order.urls'), name='order_api'),
    path('/swagger', schema_view)
]

