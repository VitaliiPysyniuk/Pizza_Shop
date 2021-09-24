from django.db import models

from .services import upload_to


class PizzaModel(models.Model):
    class Meta:
        db_table = 'pizzas'

    title = models.CharField(max_length=30, unique=True)
    ingredients = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=15)
    image = models.FileField(upload_to=upload_to)


class PizzaSizeModel(models.Model):
    class Meta:
        db_table = 'pizza_sizes'

    diameter = models.CharField(max_length=5)
    weight = models.SmallIntegerField()
    price = models.SmallIntegerField()

    pizza = models.ForeignKey(PizzaModel, on_delete=models.CASCADE, related_name='sizes')
