from django.test import TestCase
from order.factories import OrderFactory, OrderItemFactory
from billing.models import Billing, calculate_amount_total
import datetime
from member.factories import ClientFactory, RouteFactory
from order.models import Order
from django.core.urlresolvers import reverse
from billing.factories import BillingFactory


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


class BillingViewTestCase(TestCase):

    fixtures = ['routes.json']

    def test_anonymous_user_gets_redirect_to_login_page(self):
        self.client.logout()
        bill = BillingFactory()
        response = self.client.get(
            reverse(
                'billing:view',
                kwargs={'pk': bill.id}
            )
        )
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('billing:view',
                                                       kwargs={'pk': bill.id}),
            status_code=302
        )


class BillingListTestCase(TestCase):

    def test_anonymous_user_gets_redirected_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('billing:list'))
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('billing:list'),
            status_code=302
        )


class BillingFormTestCase(TestCase):

    fixtures = ['routes.json']

    def test_anonymous_user_gets_redirected_to_login_page_on_creation(self):
        self.client.logout()
        response = self.client.get(reverse('billing:create'))
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('billing:create'),
            status_code=302
        )
