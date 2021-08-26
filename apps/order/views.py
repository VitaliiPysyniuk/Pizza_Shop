from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, \
    UpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import OrderModel, OrderPizzaSizeModel
from .serializers import OrderSerializer, OrderPizzaSizeSerializer
from ..user.permissions import IsManager


class OrderListCreateView(ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.all()

    def get_queryset(self):
        user = self.request.user
        print(user)
        if user.is_anonymous:
            return OrderModel.objects.none()
        elif user.role == 'manager':
            return OrderModel.objects.all()
        elif user.role == 'courier':
            return OrderModel.objects.filter(courier_id=user.id)
        return OrderModel.objects.filter(user_id=user.id)


class OrderRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.all()


class OrderPizzaRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = OrderPizzaSizeSerializer

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        queryset = OrderPizzaSizeModel.objects.filter(order_id=order_id, id=pk)
        return queryset

