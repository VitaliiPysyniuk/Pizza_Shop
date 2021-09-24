from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.generics import ListAPIView, CreateAPIView, get_object_or_404, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import PizzaSerializer, PizzaSizeSerializer
from .models import PizzaModel, PizzaSizeModel
from ..user.permissions import IsManager


class PizzaListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = PizzaModel.objects.all()
    serializer_class = PizzaSerializer


class PizzaCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSerializer


@extend_schema_view(
    put=extend_schema(exclude=True)
)
class PizzaUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = PizzaModel.objects.all()
    serializer_class = PizzaSerializer

    def get_object(self):
        lookup_kwargs = {
            'id': self.kwargs.get('pizza_id')
        }
        return self.get_queryset().get(**lookup_kwargs)


class PizzaSizeCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSizeSerializer

    def perform_create(self, serializer):
        pizza_id = self.kwargs.get('pizza_id')
        pizza = get_object_or_404(PizzaModel, pk=pizza_id)
        serializer.save(pizza=pizza)


@extend_schema_view(
    put=extend_schema(exclude=True)
)
class PizzaSizeUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSizeSerializer
    queryset = PizzaSizeModel.objects.all()

    def get_object(self):
        lookup_kwargs = {
            'pizza_id': self.kwargs.get('pizza_id'),
            'id': self.kwargs.get('pizza_size_id')
        }
        return self.get_queryset().get(**lookup_kwargs)















