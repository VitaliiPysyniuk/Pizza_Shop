from rest_framework.generics import RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView,\
    GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..user.serializers import UserSerializer
import pytz
from django.db.models import Count, Sum, F
from datetime import datetime

from .models import OrderModel, OrderPizzaSizeModel
from .serializers import OrderSerializer, OrderPizzaSizeSerializer
from ..user.permissions import IsManager, IsCourier
from .services import GeocodingAPI

UserModel = get_user_model()


class OrderCreateView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        delivery_address = self.request.data['delivery_address']

        try:
            GeocodingAPI.validate_addresses(delivery_address)
        except ValueError as err:
            return Response({'error': str(err)}, status.HTTP_400_BAD_REQUEST)

        user = self.request.user

        if user.is_anonymous:
            user_data = self.request.data.pop('user')
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user = user_serializer.save()

        order_serializer = OrderSerializer(data=self.request.data)
        order_serializer.is_valid()
        order_serializer.save(user=user)

        return Response(order_serializer.data, status.HTTP_200_OK)


class OrderListView(ListAPIView):
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


class OrderRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    queryset = OrderModel.objects.all()

    def get_permissions(self):
        data = self.request.data

        if list(data) == ['status']:
            return [IsAuthenticated(), IsCourier()]
        return [IsAuthenticated(), IsManager()]

    def perform_update(self, serializer):
        time_fields_depend_on_status = {'confirmed': 'confirmation_time', 'in_the_road': 'delivery_start_time'}
        data = self.request.data
        if 'status' in data.keys():
            timezone = pytz.timezone('Etc/GMT-3')
            current_server_time = datetime.now(tz=timezone)

            if data['status'] == 'delivered':
                delivery_start_time = OrderSerializer(self.get_object()).data.get('delivery_start_time')
                delivery_start_time = datetime.strptime(delivery_start_time, "%Y-%m-%dT%H:%M:%S.%f%z")
                delivery_time = current_server_time - delivery_start_time
                serializer.save(delivery_time=str(delivery_time).split('.')[0])
            else:
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


class StatisticView(GenericAPIView):
    # permission_classes = [IsAuthenticated, IsManager]
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        query_params = self.request.query_params
        keys = query_params.keys()
        group_by_keys = {'title': 'pizzas__pizza_size__pizza__title', 'size': 'pizzas__pizza_size',
                         'courier': 'courier', 'week_day': 'creation_time__week_day', 'month': 'creation_time__month'}

        result = OrderModel.objects.all()

        if 'date_from' in keys and 'date_to' in keys:
            result = result.filter(creation_time__date__gte=query_params['date_from'],
                                   creation_time__date__lte=query_params['date_to'])

        if 'hour_from' in keys and 'hour_to' in keys:
            if int(query_params['hour_to']) >= int(query_params['hour_from']):
                result = result.filter(creation_time__hour__gte=query_params['hour_from'],
                                       creation_time__hour__lte=query_params['hour_to'])
            else:
                result = result.filter(creation_time__hour__gte=query_params['hour_to'],
                                       creation_time__hour__lte=query_params['hour_from'])

        if 'week_day' in keys:
            result = result.filter(creation_time__week_day=query_params['week_day'])

        if 'month' in keys:
            result = result.filter(creation_time__month=query_params['month'])

        if 'delivery_time' in keys and bool(query_params['delivery_time']):
            result = result.annotate(delivery_time=F('delivery_end_time__time') - F('delivery_start_time__time')) \
                .order_by('-delivery_time')

        if 'group' in keys:
            group_by = [group_by_keys[item] for item in query_params['group'].split(',')]
            result = result.values(*group_by)

            if 'courier' in query_params['group'].split(','):
                result = result.annotate(number_of_delivered_orders=Count('id')) \
                    .order_by('-number_of_delivered_orders')
            else:
                result = result.annotate(number_of_pizza=Sum('pizzas__number_of_pizza')).order_by('-number_of_pizza')
        else:
            result = OrderSerializer(instance=result, many=True).data

        return Response(result, status=status.HTTP_200_OK)
