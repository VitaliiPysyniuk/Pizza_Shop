from django.urls import path

from .views import UserCreateListView, CourierUpdateView

urlpatterns = [
    path('', UserCreateListView.as_view()),
    path('/<int:pk>/update', CourierUpdateView.as_view())
]
