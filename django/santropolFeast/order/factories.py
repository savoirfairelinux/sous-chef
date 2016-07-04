# coding=utf-8
import factory
from member.factories import MemberFactory, ClientFactory
from order.models import Order, Order_item

from datetime import datetime


class OrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order

    creation_date = datetime.now()
    delivery_date = datetime.now()
    client = factory.SubFactory(ClientFactory)


class OrderItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order_item
