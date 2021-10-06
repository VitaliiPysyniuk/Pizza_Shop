from rest_framework.generics import ListAPIView, CreateAPIView, get_object_or_404, RetrieveUpdateAPIView, \
    RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .serializers import PizzaSerializer, FullPizzaSerializer, PizzaSizeSerializer
from .models import PizzaModel, PizzaSizeModel
from ..user.permissions import IsManager


@extend_schema_view(
    get=extend_schema(
        summary='Get all available pizzas.',
        description='Receives all pizzas which can be ordered with a full description of every pizza and with a list of'
                    ' available sizes of pizza.'
    )
)
class PizzaListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = PizzaModel.objects.all()
    serializer_class = FullPizzaSerializer


@extend_schema_view(
    post=extend_schema(
        summary='Create new pizza.',
        description='Create new pizza.'
    )
)
class PizzaCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSerializer


@extend_schema_view(
    get=extend_schema(
        summary='Get the specific pizza.',
        description='Pizza is selected by a set parameter pizza_id. Only manager can do this.',
        parameters=[OpenApiParameter(name='pizza_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza.')
                    ]
    ),
    patch=extend_schema(
        summary='Update the specific pizza.',
        description='Pizza is selected by a set parameter pizza_id. Only manager can do this.',
        parameters=[OpenApiParameter(name='pizza_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza.')]
    ),
    put=extend_schema(exclude=True)
)
class PizzaUpdateDeleteView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    queryset = PizzaModel.objects.all()
    serializer_class = PizzaSerializer

    def get_object(self):
        lookup_kwargs = {
            'id': self.kwargs.get('pizza_id')
        }
        return self.get_queryset().get(**lookup_kwargs)


@extend_schema_view(
    post=extend_schema(
        summary='Create new pizza size.',
        description='Pizza for which size creates is selected by a set parameter pizza_id. Only manager can do this.',
        parameters=[OpenApiParameter(name='pizza_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza.')]
    )
)
class PizzaSizeCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = PizzaSizeSerializer

    def perform_create(self, serializer):
        pizza_id = self.kwargs.get('pizza_id')
        pizza = get_object_or_404(PizzaModel, pk=pizza_id)
        serializer.save(pizza=pizza)


@extend_schema_view(
    get=extend_schema(
        summary='Get the specific pizza size.',
        description='Pizza size is selected with help of two parameters pizza_id and pizza_size_id. The size which is '
                    'selected must belong to the set pizza. Only manager can do this.',
        parameters=[OpenApiParameter(name='pizza_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza.'),
                    OpenApiParameter(name='pizza_size_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza size.')]
    ),
    patch=extend_schema(
        summary='Update the specific pizza size.',
        description='Pizza size is selected with help of two parameters pizza_id and pizza_size_id. The size which is '
                    'selected must belong to the set pizza. Only manager can do this.',
        parameters=[OpenApiParameter(name='pizza_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza.')]
    ),
    delete=extend_schema(
        summary='Delete the specific pizza size.',
        description='Pizza size is selected with help of two parameters pizza_id and pizza_size_id. The size which is '
                    'selected must belong to the set pizza. Only manager can do this.',
        parameters=[OpenApiParameter(name='pizza_id', type=int, required=True, location='path',
                                     description='The id of the specific pizza.')]
    ),
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
