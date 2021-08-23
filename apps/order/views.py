from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny

from .models import OrderModel, OrderPizzaSizeModel
from .serializers import OrderSerializer, OrderPizzaSizeSerializer


class OrderListCreateView(ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer

