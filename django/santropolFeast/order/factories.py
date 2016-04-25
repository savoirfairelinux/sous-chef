# coding=utf-8
import factory
from santropolFeast.order.models import Order, OrderItem

from django.santropolFeast.member.factories import MemberFactory


class OrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order

    order_date = '01/02/2016'
    type = "paid"
    value = "1223"
    client = MemberFactory
    order_items = "main"

    @classmethod
    def __init__(self, **kwargs):
        orderItem = kwargs.pop('orderitem', None)
        order = super(OrderFactory, self).__init__(self, **kwargs)
        order.save()


class OrderItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = OrderItem
