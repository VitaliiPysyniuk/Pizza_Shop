from rest_framework.generics import RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, \
    GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..user.serializers import UserSerializer
import pytz
from django.db.models import Count, Sum, Avg
from datetime import datetime
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample

from .models import OrderModel, OrderPizzaSizeModel
from .serializers import OrderSerializer, OrderPizzaSizeSerializer
from ..user.permissions import IsManager, IsCourier
from .services import GeocodingAPI

UserModel = get_user_model()


@extend_schema_view(
    post=extend_schema(
        summary='Creates new order.',
        description='Creates a new order. If the request user is unauthorized, need to add user data to the'
                    ' request body.'
    )
)
class OrderCreateView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer

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


@extend_schema_view(
    get=extend_schema(
        summary='Get all orders.',
        description='Receives all orders that are related to the authorized user. If the authorized user is a manager, '
                    'he will receive all existing orders, if the authorized user is a courier, he will receive only '
                    'the orders he must deliver, if the authorized user is a simple user, he will receive only those '
                    'orders he created.'
    )
)
class OrderListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return OrderModel.objects.none()
        elif user.role == 'manager':
            return OrderModel.objects.all()
        elif user.role == 'courier':
            return OrderModel.objects.filter(courier_id=user.id)
        return OrderModel.objects.filter(user_id=user.id)


@extend_schema_view(
    get=extend_schema(
        summary='Get the specific order.',
        description='Order is selected by a set parameter order_id.',
        parameters=[OpenApiParameter(name='order_id', type=int, required=True, location='path',
                                     description='The id of the specific order.')]
    ),
    patch=extend_schema(
        summary='Updates the specific order.',
        description='Order is selected by a set parameter order_id. The anager can change all fields of the order, '
                    'the courier can change only the status field of the order.',
        parameters=[OpenApiParameter(name='order_id', type=int, required=True, location='path',
                                     description='The id of the specific order.')]
    ),
    put=extend_schema(exclude=True)
)
class OrderRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    queryset = OrderPizzaSizeModel.objects.all()

    def get_object(self):
        lookup_kwargs = {
            'id': self.kwargs.get('order_id')
        }
        return self.get_queryset().get(**lookup_kwargs)

    def get_permissions(self):
        data = self.request.data
        # order = get_object_or_404(OrderModel, pk=self.kwargs.get('pk'))
        #
        # if list(data) == ['status'] and self.request.user == order.courier:
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
                delivery_duration = current_server_time - delivery_start_time
                serializer.save(delivery_duration=str(delivery_duration).split('.')[0])
            else:
                time_field_to_update = time_fields_depend_on_status[data['status']]
                serializer.save(**{time_field_to_update: current_server_time})
        else:
            serializer.save()


@extend_schema_view(
    get=extend_schema(
        summary='Get information about an ordered item from the order.',
        description='Get information about ordered pizza from the order. Order is selected by a set parameter order_id.'
                    ' The pizza is selected by a set parameter pk. The information contains the id of the pizza size '
                    'and the number of ordered pizzas.',
        parameters=[
            OpenApiParameter(name='item_id', type=int, required=True, location='path',
                             description='The id of the specific item of the order.'),
            OpenApiParameter(name='order_id', type=int, required=True, location='path',
                             description='The id of the specific order.'),
        ]
    ),
    patch=extend_schema(
        summary='Updates information about an ordered item from the order.',
        description='Updates information about ordered pizza from the order. Order is selected by a set parameter '
                    'order_id. The pizza is selected by a set parameter pk. The information contains the id of the '
                    'pizza size and the number of ordered pizzas only this information can updated.',
        parameters=[
            OpenApiParameter(name='item_id', type=int, required=True, location='path',
                             description='The id of the specific item of the order.'),
            OpenApiParameter(name='order_id', type=int, required=True, location='path',
                             description='The id of the specific order.'),
        ]
    ),
    delete=extend_schema(
        summary='Delete ordered item from the order.',
        description='Delete ordered pizza from the order. Order is selected by a set parameter order_id. The pizza is '
                    'selected by a set parameter pk.',
        parameters=[
            OpenApiParameter(name='item_id', type=int, required=True, location='path',
                             description='The id of the specific item of the order.'),
            OpenApiParameter(name='order_id', type=int, required=True, location='path',
                             description='The id of the specific order.'),
        ]
    ),
    put=extend_schema(exclude=True)

)
class OrderPizzaRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = OrderPizzaSizeSerializer
    queryset = OrderPizzaSizeModel.objects.all()

    def get_object(self):
        lookup_kwargs = {
            'order_id': self.kwargs.get('order_id'),
            'id': self.kwargs.get('item_id')
        }
        return self.get_queryset().get(**lookup_kwargs)


@extend_schema_view(
    get=extend_schema(
        summary='Get statistics about orders.',
        description='Get statistic data about selected orders. Selection can be specified by the setting of query '
                    'parameters, also the result data can be grouped by the setting of the specific query parameter.',
        parameters=[
            OpenApiParameter(name='date_from', type=str, required=False, location='query',
                             description='The date from which orders are selected.',
                             examples=[OpenApiExample(name='date_to example', value='2021-09-19')]
                             ),
            OpenApiParameter(name='date_to', type=str, required=False, location='query',
                             description='The date from which orders are selected.',
                             examples=[OpenApiExample(name='date_from example', value='2021-09-21')]
                             ),
            OpenApiParameter(name='hour_from', type=int, required=False, location='query',
                             description='The hour from which orders are selected.',
                             examples=[OpenApiExample(name='hour_from example', value='11')]
                             ),
            OpenApiParameter(name='hour_to', type=int, required=False, location='query',
                             description='The hour to which orders are selected.',
                             examples=[OpenApiExample(name='hour_to example', value='18')]
                             ),
            OpenApiParameter(name='week_day', type=int, required=False, location='query',
                             description='The day of the week for selecting orders for that day.',
                             examples=[OpenApiExample(name='Sunday example', value='1'),
                                       OpenApiExample(name='Friday example', value='6')]
                             ),
            OpenApiParameter(name='month', type=int, required=False, location='query',
                             description='The number of month k for selecting orders for that month.',
                             examples=[OpenApiExample(name='September example', value='9'),
                                       OpenApiExample(name='December example', value='12')]
                             ),
            OpenApiParameter(name='group', type=str, required=False, location='query',
                             description='Parameter for grouping result can involve a few items: title - for grouping'
                                         'by the name of the pizza, size - for grouping by the size of pizza, courier -'
                                         'for grouping by the courier, week_day - for grouping by the day of the week, '
                                         'month - for grouping by the month.',
                             examples=[
                                 OpenApiExample(name='group example 1', value='title,size,courier,week_day,month'),
                                 OpenApiExample(name='group example 2', value='title,size,courier,month'),
                                 OpenApiExample(name='group example 3', value='title,courier')]
                             ),
        ]
    )
)
class StatisticView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, *args, **kwargs):
        query_params = self.request.query_params
        group_by_fields = {'title': 'pizzas__pizza_size__pizza__title', 'size': 'pizzas__pizza_size',
                           'courier': 'courier', 'week_day': 'creation_time__week_day', 'month': 'creation_time__month'}

        result = OrderModel.objects.all()

        if 'date_from' in query_params:
            result = result.filter(creation_time__date__gte=query_params['date_from'])

        if 'date_to' in query_params:
            result = result.filter(creation_time__date__lte=query_params['date_to'])

        if 'hour_from' in query_params and 'hour_to' in query_params:
            if int(query_params['hour_to']) >= int(query_params['hour_from']):
                result = result.filter(creation_time__hour__gte=query_params['hour_from'],
                                       creation_time__hour__lte=query_params['hour_to'])
            else:
                result = result.filter(creation_time__hour__gte=query_params['hour_to'],
                                       creation_time__hour__lte=query_params['hour_from'])

        if 'week_day' in query_params:
            result = result.filter(creation_time__week_day=query_params['week_day'])

        if 'month' in query_params:
            result = result.filter(creation_time__month=query_params['month'])

        if 'group' in query_params:
            group_by = [group_by_fields[field] for field in query_params['group'].split(',')]
            print(group_by)
            result = result.values(*group_by)

            if 'courier' in query_params['group'].split(','):
                result = result.annotate(number_of_delivered_orders=Count('id')) \
                    .order_by('-number_of_delivered_orders')
            else:
                result = result.annotate(number_of_pizza=Sum('pizzas__number_of_pizza')).order_by('-number_of_pizza')

            result = result.annotate(delivery_duration__avg=Avg('delivery_duration')) \
                .order_by('delivery_duration__avg')

            for item in result:
                item['delivery_duration__avg'] = str(item['delivery_duration__avg']).split('.')[0]

        else:
            result = result.order_by('delivery_duration')
            result = OrderSerializer(instance=result, many=True).data

        return Response(result, status=status.HTTP_200_OK)
