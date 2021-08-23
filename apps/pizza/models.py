from django.db import models

from .services import upload_to


class PizzaModel(models.Model):
    class Meta:
        db_table = 'pizza'

    title = models.CharField(max_length=30, unique=True)
    ingredients = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=15)
    image = models.FileField(upload_to=upload_to, default=None)


class PizzaSizeModel(models.Model):
    class Meta:
        db_table = 'pizza_size'

    diameter = models.SmallIntegerField()
    weight = models.SmallIntegerField()
    price = models.SmallIntegerField()

    pizza_id = models.ForeignKey(PizzaModel, on_delete=models.CASCADE, related_name='sizes')
