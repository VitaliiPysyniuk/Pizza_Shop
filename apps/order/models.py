from django.db import models
from datetime import time

from ..user.models import CustomUserModel
from ..pizza.models import PizzaSizeModel


class OrderModel(models.Model):
    class Meta:
        db_table = 'orders'

    status = models.CharField(max_length=24, default='created')
    creation_time = models.DateTimeField(auto_now_add=True)
    confirmation_time = models.DateTimeField(auto_now_add=True)
    delivery_start_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.TimeField(default=time())
    delivery_address = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=4)
    comment = models.CharField(max_length=200)
    total = models.SmallIntegerField(default=0)

    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='orders')
    courier = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, related_name='delivers', null=True)


class OrderPizzaSizeModel(models.Model):
    class Meta:
        db_table = 'order_pizzas'

    number_of_pizza = models.SmallIntegerField()

    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='pizzas')
    pizza_size = models.ForeignKey(PizzaSizeModel, on_delete=models.PROTECT)
