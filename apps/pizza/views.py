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


class PizzaUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = PizzaModel.objects.all()
    serializer_class = PizzaSerializer


class PizzaSizeCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSizeSerializer

    def perform_create(self, serializer):
        pizza_id = self.kwargs.get('pizza_id')
        pizza = get_object_or_404(PizzaModel, pk=pizza_id)
        serializer.save(pizza=pizza)


class PizzaSizeUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSizeSerializer

    def get_queryset(self):
        pizza_id = self.kwargs.get('pizza_id')
        pk = self.kwargs.get('pk')
        queryset = PizzaSizeModel.objects.filter(pizza_id=pizza_id, id=pk)
        return queryset














