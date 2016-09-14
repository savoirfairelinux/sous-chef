from django.test import TestCase
from order.factories import OrderFactory, OrderItemFactory
from billing.models import Billing, calculate_amount_total, BillingManager
import datetime
from member.factories import ClientFactory, RouteFactory
from order.models import Order
from django.core.urlresolvers import reverse
from billing.factories import BillingFactory


class BillingTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        cls.client1 = ClientFactory()
        cls.billed_orders = OrderFactory.create_batch(
            10,
            delivery_date=datetime.datetime.today(),
            client=cls.client1, status="D", )
        cls.orders = OrderFactory.create_batch(
            10,
            delivery_date=datetime.datetime.today(),
            client=ClientFactory(),
            status="O",
        )

    def test_get_billable_orders(self):
        """
        Test that all the delivered orders for a given month are fetched.
        """
        month = datetime.datetime.now().strftime("%m")
        year = datetime.datetime.now().strftime("%Y")
        orders = Order.objects.get_billable_orders(year, month)
        self.assertEqual(len(self.billed_orders), orders.count())

    def testTotalAmount(self):
        total_amount = calculate_amount_total(self.orders)

    def testOrderDetail(self):
        pass

    def test_get_billable_orders_client(self):
        """
        Test that all the delivered orders for a given month and
        a given client are fetched.
        """
        month = datetime.datetime.now().strftime("%m")
        year = datetime.datetime.now().strftime("%Y")
        orders = Order.objects.get_billable_orders_client(
            month, year, self.client1
        )
        self.assertEqual(len(self.billed_orders), orders.count())


class BillingManagerTestCase(TestCase):

    fixtures = ['routes.json']

    def setUp(self):
        self.today = datetime.datetime.today()
        self.billable_orders = OrderFactory.create_batch(
            10, delivery_date=self.today, status="D", )

    def test_billing_create_new(self):
        billing = Billing.objects.billing_create_new(
            self.today.year, self.today.month)
        self.assertEqual(10, billing.orders.all().count())
        self.assertEqual(self.today.month, billing.billing_month)
        self.assertEqual(self.today.year, billing.billing_year)
        # We created 10 orders, with one billable 10$ value item each
        self.assertEqual(50.00, billing.total_amount)

    def test_billing_get_period(self):
        billing = Billing.objects.billing_get_period(
            self.today.year, self.today.month)
        self.assertEqual(None, billing)


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
