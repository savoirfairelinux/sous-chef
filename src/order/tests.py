import random
import urllib.parse
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy

from member.models import Client, Address, Member
from member.factories import RouteFactory, ClientFactory
from meal.factories import ComponentFactory
from order.models import Order, Order_item
from order.factories import OrderFactory


class OrderTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        RouteFactory.create_batch(10)

    def test_get_orders_for_date(self):
        OrderFactory(delivery_date=date.today())
        self.assertTrue(
            len(
                Order.objects.get_orders_for_date(
                    delivery_date=date.today()
                )
            ) == 1
        )

    def test_order_str_includes_date(self):
        delivery_date = date.today()
        OrderFactory(delivery_date=delivery_date)
        orders = Order.objects.get_orders_for_date(
            delivery_date=delivery_date)
        self.assertTrue(str(delivery_date) in str(orders[0]))


class OrderItemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test'
        )
        address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5')
        member = Member.objects.create(firstname='Angela',
                                       lastname='Desousa',
                                       address=address
                                       )
        client = Client.objects.create(
            member=member, billing_member=member,
            birthdate=date(1980, 4, 19)
        )
        total_zero_order = Order.objects.create(
            creation_date=date(2016, 10, 5),
            delivery_date=date(2016, 10, 10),
            status='B', client=client,
        )
        Order_item.objects.create(
            order=total_zero_order,
            price=22.50,
            billable_flag=False,
            order_item_type='',
            remark="12"
        )
        order = Order.objects.create(
            creation_date=date(2016, 5, 5),
            delivery_date=date(2016, 5, 10),
            status='B', client=client,
        )
        Order_item.objects.create(
            order=order, price=6.50, billable_flag=True, order_item_type='',
            remark="testing", size="R",
        )
        Order_item.objects.create(
            order=order, price=12.50, billable_flag=False, order_item_type='',
            remark="testing", size="L",
        )

    def test_billable_flag(self):
        order = Order.objects.get(creation_date=date(2016, 5, 5))
        billable_order_item = Order_item.objects.get(order=order, price=6.50)
        self.assertEqual(billable_order_item.billable_flag, True)

    def test_non_billable_flag(self):
        order = Order.objects.get(creation_date=date(2016, 5, 5))
        non_billable_order_item = Order_item.objects.get(
            order=order,
            price=12.50
        )
        self.assertEqual(non_billable_order_item.billable_flag, False)

    def test_total_price(self):
        order = Order.objects.get(delivery_date=date(2016, 5, 10))
        self.assertEqual(order.price, 6.50)

    def test_total_price_is_zero(self):
        order = Order.objects.get(delivery_date=date(2016, 10, 10))
        self.assertEqual(order.price, 0)

    def test_order_item_remark(self):
        order = Order.objects.get(delivery_date=date(2016, 5, 10))
        order_item = order.orders.first()
        self.assertEqual(order_item.remark, 'testing')

    def test_order_item_str_includes_date(self):
        delivery_date = date(2016, 5, 10)
        order = Order.objects.get(delivery_date=delivery_date)
        order_item = order.orders.first()
        self.assertTrue(str(delivery_date) in str(order_item))


class OrderCreateOnDefaultsTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        clients = ClientFactory.create_batch(4)
        for client in clients:
            client.set_meal_defaults(
                'main_dish',
                4,
                random.choice([1, 2]),
                random.choice(['R', 'L'])
            )
            client.set_meal_defaults(
                'dessert', 4, random.choice([0, 1, 2]), ''
            )
            client.set_meal_defaults(
                'diabetic dessert', 4, random.choice([0, 1, 2]), ''
            )
            client.set_meal_defaults(
                'fruit_salad', 4, random.choice([0, 1, 2]), ''
            )
            client.set_meal_defaults(
                'green_salad', 4, random.choice([0, 1, 2]), ''
            )
            client.set_meal_defaults(
                'pudding', 4, random.choice([0, 1, 2]), ''
            )
            client.set_meal_defaults(
                'compote', 4, random.choice([0, 1, 2]), ''
            )
            client.save()

    def test_create_all_orders_fixed_date(self):
        """All orders will be created"""
        creation_date = date(2016, 7, 8)
        delivery_date = date(2016, 7, 15)
        clients = Client.objects.all()
        Order.create_orders_on_defaults(
            creation_date, delivery_date, clients)
        new = Order.objects.filter(delivery_date=delivery_date)
        self.assertEqual(len(new), len(clients))

    def test_create_only_new_orders_fixed_date(self):
        """Only new orders for delivery date will be created"""
        creation_date = date(2016, 7, 9)
        delivery_date = date(2016, 7, 15)
        clients = Client.objects.all()
        # create 2 old orders
        Order.create_orders_on_defaults(
            date(2016, 7, 5), delivery_date, clients[0:2])
        old = Order.objects.filter(delivery_date=delivery_date)
        numold = len(old)  # because query is lazy and old will change below
        # create new orders
        Order.create_orders_on_defaults(
            creation_date, delivery_date, clients)
        new = Order.objects.filter(
            creation_date=creation_date, delivery_date=delivery_date)
        # TODO improve using join on old clients
        # check that old orders not overridden
        self.assertEqual(len(new), len(clients) - numold)


class OrderFormTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        cls.order = OrderFactory.create()
        cls.admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )

    def setUp(self):
        self.client.login(username=self.admin.username, password='test1234')

    def tearDown(self):
        self.client.logout()

    def _test_order_with_errors(self, route):
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': '',
            'creation_date': '',
            'delivery_date': '',
            'status': ''
        }
        response = self.client.post(route, data, follow=True)
        self.assertTrue(b'Required information missing' in response.content)
        self.assertTrue(b'Client' in response.content)
        self.assertTrue(b'Creation date' in response.content)
        self.assertTrue(b'Delivery date' in response.content)
        self.assertTrue(b'Order status' in response.content)

    def _test_order_without_errors(self, route, client):
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': client.id,
            'creation_date': '2016-12-12',
            'delivery_date': '2016-12-22',
            'status': 'O'
        }
        response = self.client.post(route, data, follow=True)
        order = Order.objects.latest('id')
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('order:view', kwargs={'pk': order.id})
        )

    def _test_order_item_with_errors(self, route, client):

        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': client.id,
            'creation_date': '2016-12-12',
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-component': '',
            'orders-0-component_group': '',
            'orders-0-price': '',
            'orders-0-billable_flag': '',
            'orders-0-size': '',
            'orders-0-order_item_type': '',
            'orders-0-remark': 'Order item with errors',
            'orders-0-total_quantity': '',
            'orders-0-free_quantity': '',
        }
        response = self.client.post(route, data, follow=True)
        self.assertTrue(b'Required information' in response.content)
        self.assertTrue(b'Client' in response.content)
        self.assertTrue(b'Creation date' in response.content)
        self.assertTrue(b'Delivery date' in response.content)
        self.assertTrue(b'Order status' in response.content)
        self.assertTrue(b'Order item' in response.content)
        self.assertTrue(b'Component' in response.content)
        self.assertTrue(b'Component group' in response.content)
        self.assertTrue(b'Price' in response.content)
        self.assertTrue(b'Size' in response.content)
        self.assertTrue(b'Order item type' in response.content)
        self.assertTrue(b'Billable flag' in response.content)
        self.assertTrue(b'Remark' in response.content)
        self.assertTrue(b'Total quantity' in response.content)
        self.assertTrue(b'Free quantity' in response.content)

    def _test_order_item_without_errors(self, route, client, component):
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': client.id,
            'creation_date': '2016-12-12',
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-component': component.id,
            'orders-0-component_group': 'main_dish',
            'orders-0-price': '5',
            'orders-0-billable_flag': True,
            'orders-0-size': 'R',
            'orders-0-order_item_type': 'B component',
            'orders-0-remark': 'Order item without errors',
            'orders-0-total_quantity': '5',
            'orders-0-free_quantity': '3',
        }
        response = self.client.post(route, data, follow=True)
        order = Order.objects.latest('id')
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('order:view', kwargs={'pk': order.id})
        )


class OrderCreateFormTestCase(OrderFormTestCase):

    def test_access_to_create_form(self):
        """Test if the form is accessible from its url"""
        response = self.client.get(
            reverse_lazy(
                'order:create'
            ), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_create_form_validate_data(self):
        """Test all the step of the form with and without wrong data"""
        client = ClientFactory()
        component = ComponentFactory(name="Component create validate test")
        route = reverse_lazy('order:create')
        self._test_order_with_errors(route)
        self._test_order_without_errors(route, client)
        self._test_order_item_with_errors(route, client)
        self._test_order_item_without_errors(route, client, component)

    def test_create_form_save_data(self):
        client = ClientFactory()
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': client.id,
            'creation_date': '2016-12-12',
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-component_group': 'main_dish',
            'orders-0-price': '5',
            'orders-0-billable_flag': True,
            'orders-0-size': 'R',
            'orders-0-order_item_type': 'B component',
            'orders-0-remark': 'Order item without errors',
            'orders-0-total_quantity': '5',
            'orders-0-free_quantity': '3',
        }
        self.client.post(
            reverse('order:create'),
            data,
            follow=True
        )
        order = Order.objects.latest('id')
        self.assertEqual(order.client.id, client.id)
        self.assertEqual(order.orders.first().component_group, 'main_dish')
        self.assertEqual(order.creation_date, date(2016, 12, 12))
        self.assertEqual(order.delivery_date, date(2016, 12, 22))
        self.assertEqual(order.price, 5)
        self.assertEqual(order.orders.first().billable_flag, True)
        self.assertEqual(order.orders.first().size, 'R')
        self.assertEqual(order.orders.first().order_item_type, 'B component')
        self.assertEqual(
            order.orders.first().remark,
            'Order item without errors'
        )
        self.assertEqual(order.orders.first().total_quantity, 5)
        self.assertEqual(order.orders.first().free_quantity, 3)


class OrderUpdateFormTestCase(OrderFormTestCase):

    def test_access_to_update_form(self):
        """Test if the form is accessible from its url"""
        response = self.client.get(
            reverse_lazy(
                'order:update',
                kwargs={'pk': self.order.id}
            ), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_update_form_validate_data(self):
        """Test all the step of the form with and without wrong data"""
        client = ClientFactory()
        component = ComponentFactory(name="Component update validate test")
        route = reverse_lazy('order:update', kwargs={'pk': self.order.id})
        self._test_order_with_errors(route)
        self._test_order_without_errors(route, client)
        self._test_order_item_with_errors(route, client)
        self._test_order_item_without_errors(route, client, component)

    def test_update_status_ajax(self):
        data = {'status': 'D'}  # Delivery
        response = self.client.post(
            reverse('order:update_status', kwargs={'pk': self.order.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertTrue(response.status_code, 200)
        self.assertTrue(b'"pk":' in response.content)

    def test_update_form_save_data(self):
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': self.order.client.id,
            'creation_date': '2016-12-12',
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-id': self.order.orders.first().id,
            'orders-0-component_group': 'main_dish',
            'orders-0-price': '5',
            'orders-0-billable_flag': True,
            'orders-0-size': 'R',
            'orders-0-order_item_type': 'B component',
            'orders-0-remark': 'Order item without errors',
            'orders-0-total_quantity': '5',
            'orders-0-free_quantity': '3',
        }
        self.client.post(
            reverse_lazy('order:update', kwargs={'pk': self.order.id}),
            data,
            follow=True
        )
        order = Order.objects.get(id=self.order.id)
        self.assertEqual(order.creation_date, date(2016, 12, 12))
        self.assertEqual(order.delivery_date, date(2016, 12, 22))
        self.assertEqual(order.orders.latest('id').price, 5)
        self.assertEqual(order.orders.latest('id').billable_flag, True)
        self.assertEqual(order.orders.latest('id').size, 'R')
        self.assertEqual(
            order.orders.latest('id').order_item_type,
            'B component'
        )
        self.assertEqual(
            order.orders.latest('id').remark,
            'Order item without errors'
        )
        self.assertEqual(order.orders.latest('id').total_quantity, 5)
        self.assertEqual(order.orders.latest('id').free_quantity, 3)


class DeleteOrderTestCase(OrderFormTestCase):

    def test_confirm_delete_order(self):
        response = self.client.get(
            reverse('order:delete', args=(self.order.id,)),
            follow=True
        )
        self.assertContains(response, 'Delete Order #{}'.format(self.order.id))

    def test_delete_order(self):
        # The template will POST with a 'next' parameter, which is the URL to
        # follow on success.
        next_value = '?name=&status=O&delivery_date='
        response = self.client.post(
            (reverse('order:delete', args=(self.order.id,)) + '?next=' +
                reverse('order:list') + urllib.parse.quote_plus(next_value)),
            follow=True
        )
        self.assertRedirects(response, reverse('order:list') + next_value,
                             status_code=302)
