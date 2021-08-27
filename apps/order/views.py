from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import datetime
import pytz

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

    def perform_update(self, serializer):
        tine_fields_depend_on_status = {'confirmed': 'confirmation_time', 'in_the_road': 'delivery_start_time',
                                        'delivered': 'delivery_end_time'}
        data = self.request.data
        if 'status' in data.keys():
            timezone = pytz.timezone('Etc/GMT-3')
            current_server_time = datetime.now(tz=timezone)
            time_field_to_update = tine_fields_depend_on_status[data['status']]
            serializer.save(**{time_field_to_update: current_server_time})
        else:
            serializer.save()


class OrderPizzaRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = OrderPizzaSizeSerializer

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        queryset = OrderPizzaSizeModel.objects.filter(order_id=order_id, id=pk)
        return queryset
