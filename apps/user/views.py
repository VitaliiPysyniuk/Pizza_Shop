from django.contrib.auth import get_user_model
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


class UserRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_permissions(self):
        keys = self.request.data.keys()
        print(self.request.user.id + 1000)
        if ('role' in keys) or ('is_active' in keys) or (self.request.user.id == self.kwargs.get('pk')):
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]


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
        print(self.request.data)
        user_id = self.kwargs.get('user_id')
        serializer.save(user_id=user_id)


class UserFavoriteDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        queryset = UserFavoritesModel.objects.filter(pk=pk)
        return queryset


class CourierDeliveriesSortView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCourier]

    def get(self, *args, **kwargs):
        user = self.request.user
        courier_orders = OrderModel.objects.filter(courier_id=user.id)
        addresses = list()
        for order in courier_orders:
            addresses.append(order.delivery_address)

        params = {
            'start_address': '|'.join(addresses),
            'end_addresses': '|'.join(addresses)
        }

        maps_api_result = MapsAPIUse.get_distance_and_duration_between_addresses(**params)
        duration_matrix = maps_api_result['duration_matrix']

        solver = Solver(duration_matrix)
        solver_result = solver.branch_and_bound_method()

        route = list()
        for way in solver_result['tour']:
            route.append({'from': addresses[way['from']], 'to': addresses[way['to']]})

        return Response(route, status.HTTP_200_OK)
