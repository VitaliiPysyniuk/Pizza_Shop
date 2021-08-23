from rest_framework.serializers import ModelSerializer

from .models import PizzaModel, PizzaSizeModel


class PizzaSizeSerializer(ModelSerializer):
    class Meta:
        model = PizzaSizeModel
        fields = ['id', 'diameter', 'weight', 'price', 'pizza_id']
        extra_kwargs = {'pizza_id': {'read_only': True}}


class PizzaSerializer(ModelSerializer):
    sizes = PizzaSizeSerializer(many=True)

    class Meta:
        model = PizzaModel
        fields = ['id', 'title', 'ingredients', 'image', 'sizes']
        extra_kwargs = {'sizes': {'read_only': True}}





