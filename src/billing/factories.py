import factory
import random
from billing.models import Billing, OrderBilling
from member.factories import ClientFactory
from order.factories import OrderFactory


class BillingFactory(factory.DjangoModelFactory):

    class Meta:
        model = Billing

    client = ClientFactory()

    total_amount = random.randrange(1, stop=75, step=1)

    billing_month = random.randrange(1, stop=12, step=1)

    billing_year = random.randrange(2016, stop=2020, step=1)

    detail = {"123": 123}


class BillingOrder(factory.DjangoModelFactory):
    billing_id = BillingFactory()

    order_id = OrderFactory()
