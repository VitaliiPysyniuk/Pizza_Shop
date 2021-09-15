from rest_framework.serializers import ModelSerializer

from .models import OrderModel, OrderPizzaSizeModel
from ..user.serializers import UserSerializer
from ..pizza.serializers import PizzaSizeSerializer


class OrderPizzaSizeSerializer(ModelSerializer):
    class Meta:
        model = OrderPizzaSizeModel
        fields = ['id', 'order', 'pizza_size', 'number_of_pizza']
        extra_kwargs = {'order': {'read_only': True}}


class OrderSerializer(ModelSerializer):
    pizzas = OrderPizzaSizeSerializer(many=True)

    class Meta:
        model = OrderModel
        fields = ['id', 'user', 'courier', 'status', 'creation_time', 'confirmation_time', 'delivery_start_time',
                  'delivery_end_time', 'delivery_address', 'payment_method', 'comment', 'total', 'pizzas']
        extra_kwargs = {'courier': {'required': False}, 'total': {'read_only': True}, 'user': {'read_only': True}}

    def create(self, validated_data):
        pizzas = list(validated_data.pop('pizzas'))
        order = OrderModel.objects.create(**validated_data)
        total = 0
        for pizza in pizzas:
            pizza_size_serializer = PizzaSizeSerializer(pizza['pizza_size'])
            pizza['pizza_size'] = pizza_size_serializer.data.get('id')
            serializer = OrderPizzaSizeSerializer(data=pizza)
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order)
            total += pizza_size_serializer.data.get('price') * pizza['number_of_pizza']
        order.total = total

        return order

