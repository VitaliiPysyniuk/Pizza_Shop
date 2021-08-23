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


class PizzaSizeCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSizeSerializer

    def perform_create(self, serializer):
        pk = self.kwargs.get('pk')
        print(pk)
        pizza = get_object_or_404(PizzaModel, pk=pk)
        serializer.save(pizza=pizza)


class PizzaUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = PizzaModel.objects.all()
    serializer_class = PizzaSerializer


class PizzaSizeUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = PizzaModel.objects.all()
    serializer_class = PizzaSizeSerializer

    def get_object(self):
        pk = self.request.data['id']
        size = get_object_or_404(PizzaSizeModel, pk=pk)
        return size










