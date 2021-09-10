from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, \
    GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from datetime import datetime
from ..user.serializers import UserSerializer
import pytz

from .models import OrderModel, OrderPizzaSizeModel
from .serializers import OrderSerializer, OrderPizzaSizeSerializer
from ..user.permissions import IsManager, IsCourier

UserModel = get_user_model()


class OrderCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_anonymous:
            user_data = self.request.data.pop('user')
            print(user_data)
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()

        serializer.save(user=user)


class OrderListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return OrderModel.objects.none()
        elif user.role == 'manager':
            return OrderModel.objects.all()
        elif user.role == 'courier':
            return OrderModel.objects.filter(courier_id=user.id)
        return OrderModel.objects.filter(user_id=user.id)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class OrderRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.all()

    def get_permissions(self):
        data = self.request.data

        if data.keys() == ['status']:
            return [IsAuthenticated(), IsCourier()]
        return [IsAuthenticated(), IsManager()]

    def perform_update(self, serializer):
        time_fields_depend_on_status = {'confirmed': 'confirmation_time', 'in_the_road': 'delivery_start_time',
                                        'delivered': 'delivery_end_time'}
        data = self.request.data
        if 'status' in data.keys():
            timezone = pytz.timezone('Etc/GMT-3')
            current_server_time = datetime.now(tz=timezone)
            time_field_to_update = time_fields_depend_on_status[data['status']]
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


class OrderShortDistanceDeliveryView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCourier]

    def get(self, *args, **kwargs):
        courier = self.request.user
        return Response([], status.HTTP_200_OK)
