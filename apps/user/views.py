from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import ListCreateAPIView, DestroyAPIView, RetrieveUpdateAPIView, ListAPIView, \
    GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer, UserFavoritesSerializer
from .models import UserFavoritesModel
from .permissions import IsManager, IsCourier
from ..order.models import OrderModel
from .services import MapsAPIUse, Solver

UserModel = get_user_model()


class UserCreateListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


@extend_schema_view(
    put=extend_schema(exclude=True)
)
class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserModel.objects.all()

    def get_permissions(self):
        keys = self.request.data.keys()
        if ('role' in keys) or ('is_active' in keys) or (self.request.user.id == self.kwargs.get('pk')):
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    def get_object(self):
        lookup_kwargs = {
            'id': self.kwargs.get('user_id')
        }
        return self.get_queryset().get(**lookup_kwargs)


class UserFavoritesListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = UserFavoritesModel.objects.all()
    serializer_class = UserFavoritesSerializer


class UserFavoritesListCreateView(ListCreateAPIView):
    serializer_class = UserFavoritesSerializer

    def get_permissions(self):
        user = self.request.user
        user_id = self.kwargs.get('user_id')
        if user.id == user_id:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        queryset = UserFavoritesModel.objects.filter(user_id=user_id)
        return queryset

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        serializer.save(user_id=user_id)


class UserFavoriteDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserFavoritesModel.objects.all()

    def get_object(self):
        lookup_kwargs = {
            'user_id': self.kwargs.get('user_id'),
            'id': self.kwargs.get('favorite_id')
        }
        return self.get_queryset().get(**lookup_kwargs)


class CourierDeliveriesSortView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCourier]

    def get(self, *args, **kwargs):
        user = self.request.user
        courier_orders = OrderModel.objects.filter(courier_id=user.id)
        addresses = ['Шараневича 28, Львів']
        for order in courier_orders:
            addresses.append(order.delivery_address)

        params = {
            'addresses': '|'.join(addresses),
            'mode': 'driving'
        }

        maps_api_result = MapsAPIUse.get_value_matrix_between_addresses(**params)
        duration_matrix = maps_api_result['duration_matrix']

        solver = Solver(duration_matrix)
        solver_result = solver.branch_and_bound_method()

        tour = solver_result['tour']
        route = list()
        route_points = list()
        previous_place = 0
        i = 0

        while tour:
            if tour[i]['from'] == previous_place:
                route.append({'from': addresses[tour[i]['from']], 'to': addresses[tour[i]['to']]})
                route_points.append(addresses[tour[i]['from']])
                previous_place = tour[i]['to']
                tour.pop(i)
                i = 0
                continue
            i += 1

        route_points.append(route[-1]['to'])

        # result = {'route_points': route_points, 'route': route}
        result = {'route_points': route_points}
        return Response(result, status.HTTP_200_OK)
