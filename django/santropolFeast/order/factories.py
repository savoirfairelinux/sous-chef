# coding=utf-8
import factory
from santropolFeast.order.models import Order, OrderItem


class OrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order

    order_date = '01/02/2016'
    type = "paid"
    value = "1223"
    client = MemberFactory
    order_items = "main"


class OrderItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = OrderItem
