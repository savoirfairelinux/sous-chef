import factory
import random
import datetime
from billing.models import Billing
from member.factories import ClientFactory
from order.factories import OrderFactory


class BillingFactory(factory.DjangoModelFactory):

    class Meta:
        model = Billing

    total_amount = random.randrange(1, stop=75, step=1)
    billing_month = random.randrange(1, stop=12, step=1)
    billing_year = random.randrange(2016, stop=2020, step=1)
    detail = {}
