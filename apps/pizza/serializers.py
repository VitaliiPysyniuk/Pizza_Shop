from rest_framework.serializers import ModelSerializer

from .models import PizzaModel, PizzaSizeModel


class PizzaSizeSerializer(ModelSerializer):

    class Meta:
        model = PizzaSizeModel
        fields = ['id', 'diameter', 'weight', 'price', 'pizza']
        extra_kwargs = {'pizza': {'read_only': True}}


class PizzaSerializer(ModelSerializer):
    sizes = PizzaSizeSerializer(many=True, required=False)

    class Meta:
        model = PizzaModel
        fields = ['id', 'title', 'ingredients', 'image', 'sizes']
        extra_kwargs = {'sizes': {'read_only': True}}





