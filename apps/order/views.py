from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import OrderModel, OrderPizzaSizeModel
from .serializers import OrderSerializer, OrderPizzaSizeSerializer
from ..user.permissions import IsManager


class OrderListCreateView(ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer


class OrderRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer


class OrderPizzaRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = OrderPizzaSizeModel.objects.all()
    serializer_class = OrderPizzaSizeSerializer

