from django.db import models

from ..user.models import CustomUserModel
from ..pizza.models import PizzaSizeModel


class OrderModel(models.Model):
    class Meta:
        db_table = 'order'

    status = models.CharField(max_length=11)
    creation_time = models.DateTimeField(auto_created=True)
    confirmation_time = models.DateTimeField()
    delivery_start_time = models.DateTimeField()
    delivery_end_time = models.DateTimeField()
    delivery_address = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=4)
    comment = models.CharField(max_length=200)

    user_id = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='orders')
    courier_id = models.ForeignKey(CustomUserModel, on_delete=models.PROTECT, related_name='delivers')


class OrderPizzaSizeModel(models.Model):
    class Meta:
        db_table = 'order_pizza'

    number_of_pizza = models.SmallIntegerField()

    order_id = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='pizzas')
    pizza_size_id = models.ForeignKey(PizzaSizeModel, on_delete=models.PROTECT)
