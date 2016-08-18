from django.test import TestCase
from order.factories import OrderFactory, OrderItemFactory
from billing.models import Billing, calculate_amount_total
import datetime
from member.factories import ClientFactory, RouteFactory
from order.models import Order


class TestBilling(TestCase):

    @classmethod
    def setUpTestData(cls):
        RouteFactory.create_batch(10)

    def testTotalAmount(self):
        order = OrderFactory(delivery_date=datetime.datetime.today())
        orders = []
        orders.append(order)

        total_amount = calculate_amount_total(orders)

        self.assertEqual(total_amount, order.price)

    def testOrderDetail(self):
        pass

    def testGetOrderForMonth(self):

        order = OrderFactory(
            delivery_date=datetime.datetime.today(), status="D"
            )
        month = datetime.datetime.now().strftime("%m")
        print(month)
        year = datetime.datetime.now().strftime("%y")
        print(year)
        orders = Order.objects.get_orders_for_month(month, year)

        self.assertTrue(order, orders.first())

    def testGetOrderForMonthClient(self):
        order = OrderFactory(
            client=ClientFactory(), delivery_date=datetime.datetime.today()
            )
        month = datetime.datetime.now().strftime("%m")
        print(month)
        year = datetime.datetime.now().strftime("%y")
        print(year)
        orders = Order.objects.get_orders_for_month_client(
            month, year, order.client
            )

        self.assertTrue(order, orders.first())
