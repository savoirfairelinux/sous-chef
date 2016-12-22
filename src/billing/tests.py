from django.test import TestCase
from order.factories import OrderFactory, OrderItemFactory
from billing.models import Billing, calculate_amount_total, BillingManager
import datetime
import importlib
from member.factories import ClientFactory, RouteFactory
from order.models import Order
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from billing.factories import BillingFactory
from sous_chef.tests import TestMixin as SousChefTestMixin


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


class RedirectAnonymousUserTestCase(SousChefTestMixin, TestCase):

    fixtures = ['routes.json']

    def test_anonymous_user_gets_redirect_to_login_page(self):
        check = self.assertRedirectsWithAllMethods
        check(reverse('billing:list'))
        check(reverse('billing:create'))
        check(reverse('billing:add'))
        bill = BillingFactory()
        check(reverse('billing:view', kwargs={'pk': bill.id}))
        check(reverse('billing:delete', kwargs={'pk': bill.id}))


class BillingListViewTestCase(SousChefTestMixin, TestCase):
    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('billing:list')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('billing:list')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class BillingCreateViewTestCase(SousChefTestMixin, TestCase):
    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('billing:create')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('billing:create')
        # Run
        response = self.client.get(
            url, {'delivery_date': '2016-1'}, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain[-1][0], reverse('billing:list'))


class BillingAddViewTestCase(SousChefTestMixin, TestCase):
    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('billing:add')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('billing:add')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class BillingSummaryViewTestCase(SousChefTestMixin, TestCase):
    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        bill = BillingFactory()
        url = reverse('billing:view', args=(bill.id, ))
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        bill = BillingFactory()
        url = reverse('billing:view', args=(bill.id, ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class BillingDeleteViewTestCase(SousChefTestMixin, TestCase):
    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        bill = BillingFactory()
        url = reverse('billing:delete', args=(bill.id, ))
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        bill = BillingFactory()
        url = reverse('billing:delete', args=(bill.id, ))
        # Run
        response = self.client.post(url, {'next': '/'}, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)
