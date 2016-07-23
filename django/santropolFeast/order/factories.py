# coding=utf-8
import factory
import random
from faker import Factory as FakerFactory
from member.factories import MemberFactory, ClientFactory
from order.models import (
    Order, Order_item, ORDER_STATUS_CHOICES, ORDER_ITEM_TYPE_CHOICES
)
from meal.factories import ComponentFactory
from order.models import SIZE_CHOICES


fake = FakerFactory.create()


class OrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order

    creation_date = factory.LazyAttribute(
        lambda x: fake.date_time_between(
            start_date="-1y",
            end_date="+1y",
            tzinfo=None
        )
    )

    delivery_date = factory.LazyAttribute(
        lambda x: fake.date_time_between(
            start_date="-1y",
            end_date="+1y",
            tzinfo=None
        )
    )

    status = factory.LazyAttribute(
        lambda x: random.choice(ORDER_STATUS_CHOICES)[0]
    )

    client = factory.SubFactory(ClientFactory)

    order_item = factory.RelatedFactory(
        'order.factories.OrderItemFactory',
        'order'
    )


class OrderItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = Order_item

    order = factory.SubFactory(OrderFactory)

    component = factory.SubFactory(ComponentFactory)

    price = fake.random_int(min=0, max=50)

    billable_flag = fake.random_sample(
        elements=(True, False),
        length=None
    )

    size = factory.LazyAttribute(
        lambda x: random.choice(SIZE_CHOICES)[0]
    )

    order_item_type = factory.LazyAttribute(
        lambda x: random.choice(ORDER_ITEM_TYPE_CHOICES)[0]
    )

    remark = fake.sentence(nb_words=6, variable_nb_words=True)

    total_quantity = fake.random_digit()

    free_quantity = fake.random_digit()
