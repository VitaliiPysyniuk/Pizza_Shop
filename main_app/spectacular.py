from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.urls import path

urlpatterns = [
    path('schema', SpectacularAPIView.as_view(), name='schema'),
    path('swagger', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    # path('schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

