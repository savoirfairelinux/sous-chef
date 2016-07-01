# coding=utf-8
import factory
from member.factories import MemberFactory
from order.models import Order, Order_item


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
        model = Order_item
