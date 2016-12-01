# -*- coding: utf-8 -*-

import random
import urllib.parse
import random
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

from member.models import Client, Address, Member, Route
from member.factories import RouteFactory, ClientFactory
from meal.factories import ComponentFactory
from order.models import Order, Order_item, MAIN_PRICE_DEFAULT, \
    OrderStatusChange
from order.factories import OrderFactory


class OrderTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        """
        Provides an order Object, without any items.
        """
        cls.order = OrderFactory(order_item=None)

    def test_order_add_item_meal_component(self):
        """
        Add a billable meal component item to an order.
        """
        self.order.add_item(
            'B component',
            component_group='main_dish',
            total_quantity=2,
            size='L')
        self.assertEqual(1, self.order.orders.count())
        item = self.order.orders.filter(order_item_type='B component').get()
        self.assertTrue(item.billable_flag)
        self.assertEqual(item.component_group, 'main_dish')
        self.assertEqual(item.total_quantity, 2)
        self.assertEqual(item.size, 'L')
        self.assertEqual(item.price, MAIN_PRICE_DEFAULT * 2)

    def test_order_add_item_visit(self):
        """
        Add a non-billable visit item to an order.
        """
        self.order.add_item('N delivery',
                            billable=False)
        self.assertEqual(1, self.order.orders.count())
        item = self.order.orders.filter(order_item_type='N delivery').get()
        self.assertFalse(item.billable_flag)
        self.assertEqual(item.total_quantity, 1)
        self.assertEqual(item.price, 0)


class OrderManagerTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        cls.route = Route.objects.get(id=1)
        cls.orders = OrderFactory.create_batch(
            10, delivery_date=date.today(),
            status='O', client__route=cls.route)
        cls.past_order = OrderFactory(
            delivery_date=date(2015, 7, 15), status='O'
        )

    def test_get_shippable_orders(self):
        """
        Should return all shippable orders for the given date.
        A shippable order must be created in the database, and its ORDER_STATUS
        must be 'O' (Ordered).
        """
        orders = Order.objects.get_shippable_orders()
        self.assertEqual(len(orders), len(self.orders))
        past_order = Order.objects.get_shippable_orders(date(2015, 7, 15))
        self.assertEqual(len(past_order), 1)

    def test_get_shippable_orders_by_route(self):
        """
        Should return all shippable orders for the given route.
        A shippable order must be created in the database, and its ORDER_STATUS
        must be 'O' (Ordered).
        """
        orders = Order.objects.get_shippable_orders_by_route(self.route.id)
        self.assertEqual(len(orders), len(self.orders))

    def test_order_str_includes_date(self):
        delivery_date = date.today()
        OrderFactory(delivery_date=delivery_date)
        orders = Order.objects.get_shippable_orders(
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
        cls.total_zero_order = Order.objects.create(
            creation_date=date(2016, 10, 5),
            delivery_date=date(2016, 10, 10),
            status='B', client=client,
        )
        Order_item.objects.create(
            order=cls.total_zero_order,
            price=22.50,
            billable_flag=False,
            order_item_type='',
            remark="12"
        )
        cls.order = Order.objects.create(
            delivery_date=date(2016, 5, 10),
            status='B', client=client,
        )
        Order_item.objects.create(
            order=cls.order,
            price=6.50,
            billable_flag=True,
            order_item_type='',
            remark="testing",
            size="R",
        )
        Order_item.objects.create(
            order=cls.order,
            price=12.50,
            billable_flag=False,
            order_item_type='',
            remark="testing",
            size="L",
        )

    def test_billable_flag(self):
        billable_order_item = Order_item.objects.get(
            order=self.order, price=6.50)
        self.assertEqual(billable_order_item.billable_flag, True)

    def test_non_billable_flag(self):
        non_billable_order_item = Order_item.objects.get(
            order=self.order,
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
        """
        Create active ongoing clients with predefined meals default.
        """
        meals_default = {
            'main_dish_friday_quantity': 2,
            'size_friday': 'L',
            'dessert_friday_quantity': 0,
            'diabetic_dessert_friday_quantity': 0,
            'fruit_salad_friday_quantity': 1,
            'green_salad_friday_quantity': 0,
            'pudding_friday_quantity': 1,
            'compote_friday_quantity': 0,
        }
        cls.ongoing_clients = ClientFactory.create_batch(
            4,
            status=Client.ACTIVE,
            delivery_type='O',
            meal_default_week=meals_default)
        cls.episodic_clients = ClientFactory.create_batch(
            6, status=Client.ACTIVE, delivery_type='E')
        # The delivery date must be a Friday, to match the meals defaults
        cls.delivery_date = date(2016, 7, 15)

    def test_auto_create_orders(self):
        """
        One order per active ongoing client must have been created.
        """
        count = Order.objects.auto_create_orders(
            self.delivery_date, self.ongoing_clients)
        self.assertEqual(count, len(self.ongoing_clients))
        created = Order.objects.filter(delivery_date=self.delivery_date)
        self.assertEqual(created.count(), len(self.ongoing_clients))

    def test_auto_create_orders_existing_order(self):
        """
        Only new orders for delivery date should be created.
        """
        # Create an  for a random ongoing client
        client = random.choice(self.ongoing_clients)
        order = OrderFactory(
            delivery_date=self.delivery_date,
            client=client,
        )
        Order.objects.auto_create_orders(
            self.delivery_date, self.ongoing_clients)
        self.assertEqual(Order.objects.filter(client=client).count(), 1)

    def test_auto_create_orders_items(self):
        """
        Orders must be created with the meals defaults.
        """
        # Create orders for my ongoing active clients
        Order.objects.auto_create_orders(
            self.delivery_date, self.ongoing_clients)
        client = random.choice(self.ongoing_clients)
        order = Order.objects.filter(client=client).get()
        items = order.orders.all()
        self.assertEqual(items.count(), 3)
        main_dish_item = items.filter(component_group='main_dish').get()
        self.assertEqual(main_dish_item.total_quantity, 2)
        self.assertEqual(main_dish_item.size, 'L')
        self.assertTrue(main_dish_item.billable_flag)
        pudding_item = items.filter(component_group='pudding').get()
        self.assertEqual(pudding_item.total_quantity, 1)
        fruit_salad_item = items.filter(component_group='fruit_salad').get()
        self.assertEqual(fruit_salad_item.total_quantity, 1)
        self.assertEqual(items.filter(component_group='compote').count(), 0)


class OrderCreateBatchTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        """
        Get an episodic client, three delivery dates and several order items.
        """
        cls.orditems = {
            'main_dish_default_quantity': 1,
            'size_default': 'L',
            'dessert_default_quantity': 1,
            'diabetic_default_quantity': None,
            'fruit_salad_default_quantity': None,
            'green_salad_default_quantity': 1,
            'pudding_default_quantity': None,
            'compote_default_quantity': None,
        }
        cls.episodic_client = ClientFactory.create_batch(
            1, status=Client.ACTIVE, delivery_type='E')
        # The delivery date must be a Friday, to match the meals defaults
        cls.delivery_dates = ['2016-12-12', '2016-12-14', '2016-12-15']

    def test_create_batch_orders(self):
        """
        Provide a client, 3 delivery dates and 3 order items.
        """
        counter = Order.objects.create_batch_orders(
            self.delivery_dates, self.episodic_client[0], self.orditems)
        self.assertEqual(counter, 3)
        counter = Order.objects.create_batch_orders(
            self.delivery_dates, self.episodic_client[0], self.orditems)
        self.assertEqual(counter, 0)


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
        content = str(response.content)
        self.assertTrue(content.find('Required information missing'))
        self.assertTrue(content.find('Client'))
        self.assertTrue(content.find('Creation date'))
        self.assertTrue(content.find('Delivery date'))
        self.assertTrue(content.find('Order status'))

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
        content = str(response.content)
        order = Order.objects.latest('id')
        self.assertTrue(content.find('Required information') == -1)
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
        }
        response = self.client.post(route, data, follow=True)
        content = str(response.content)
        self.assertTrue(content.find('Required information'))
        self.assertTrue(content.find('Client'))
        self.assertTrue(content.find('Creation date'))
        self.assertTrue(content.find('Delivery date'))
        self.assertTrue(content.find('Order status'))
        self.assertTrue(content.find('Order item'))
        self.assertTrue(content.find('Component'))
        self.assertTrue(content.find('Component group'))
        self.assertTrue(content.find('Price'))
        self.assertTrue(content.find('Size'))
        self.assertTrue(content.find('Order item type'))
        self.assertTrue(content.find('Billable flag'))
        self.assertTrue(content.find('Remark'))
        self.assertTrue(content.find('Total quantity'))
        self.assertTrue(content.find('Free quantity'))

    def _test_order_item_without_errors(self, route, client, component):
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': client.id,
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-component': component.id,
            'orders-0-component_group': 'main_dish',
            'orders-0-price': '5',
            'orders-0-billable_flag': True,
            'orders-0-size': 'R',
            'orders-0-order_item_type': 'meal_component',
            'orders-0-remark': 'Order item without errors',
            'orders-0-total_quantity': '5',
        }
        response = self.client.post(route, data, follow=True)
        order = Order.objects.latest('id')
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse('order:view', kwargs={'pk': order.id})
        )


class OrderListTestCase(TestCase):

    def test_anonymous_user_gets_redirected_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('order:list'))
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('order:list'),
            status_code=302
        )


class OrderStatusChangeTestCase(OrderItemTestCase):

    def setUp(self):
        order = self.order
        order.status = 'B'
        order.save()

    def test_valid_creation_changes_order_status(self):
        order = self.order
        osc = OrderStatusChange(
            order=order,
            status_from='B',
            status_to='D'
        )
        osc.save()
        order.refresh_from_db()
        self.assertEqual(order.status, 'D')

    def test_invalid_creation_wrong_status_from(self):
        order = self.order
        with self.assertRaises(ValidationError) as context:
            osc = OrderStatusChange(
                order=order,
                status_from='D',
                status_to='N'
            )
            osc.save()

    def test_reason_field_bilingual(self):
        order = self.order
        reason = "ôn pàrlé «frânçaîs» èù£¤¢¼½¾³²±"
        osc = OrderStatusChange.objects.create(
            order=order,
            status_from='B',
            status_to='D',
            reason=reason
        )
        osc.refresh_from_db()
        self.assertEqual(osc.reason, reason)


class OrderStatusChangeViewTestCase(OrderItemTestCase):

    def setUp(self):
        order = self.order
        order.status = 'B'
        order.save()
        self.client.force_login(self.admin)

    def test_get_page(self):
        response = self.client.get(
            reverse('order:update_status', kwargs={'pk': self.order.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_update_status(self):
        data = {
            'order': self.order.pk,
            'status_to': 'D',
            'status_from': 'B'
        }
        response = self.client.post(
            reverse('order:update_status', kwargs={'pk': self.order.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        # create successful. Returns json
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'D')

    def test_no_charge_requires_a_reason(self):
        data = {
            'order': self.order.pk,
            'status_to': 'N',
            'status_from': 'B'
        }
        response = self.client.post(
            reverse('order:update_status', kwargs={'pk': self.order.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertTrue(b"errorlist" in response.content)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'B')


class OrderCreateFormTestCase(OrderFormTestCase):

    def test_access_to_create_form(self):
        """Test if the form is accessible from its url"""
        response = self.client.get(
            reverse_lazy(
                'order:create'
            ), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_gets_redirected_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('order:create'))
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('order:create'),
            status_code=302
        )

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
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-component_group': 'main_dish',
            'orders-0-price': '5',
            'orders-0-billable_flag': True,
            'orders-0-size': 'R',
            'orders-0-order_item_type': 'meal_component',
            'orders-0-remark': 'Order item without errors',
            'orders-0-total_quantity': '5',
        }
        self.client.post(
            reverse('order:create'),
            data,
            follow=True
        )
        order = Order.objects.latest('id')
        self.assertEqual(order.client.id, client.id)
        self.assertEqual(order.orders.first().component_group, 'main_dish')
        self.assertEqual(order.creation_date, date.today())
        self.assertEqual(order.delivery_date, date(2016, 12, 22))
        self.assertEqual(order.price, 5)
        self.assertEqual(order.orders.first().billable_flag, True)
        self.assertEqual(order.orders.first().size, 'R')
        self.assertEqual(order.orders.first().order_item_type,
                         'meal_component')
        self.assertEqual(
            order.orders.first().remark,
            'Order item without errors'
        )
        self.assertEqual(order.orders.first().total_quantity, 5)


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

    def test_anonymous_user_gets_redirected_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('order:update',
                                           kwargs={'pk': self.order.id}))
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('order:update',
                                                       kwargs={
                                                           'pk': self.order.id
                                                       }),
            status_code=302
        )

    def test_update_form_validate_data(self):
        """Test all the step of the form with and without wrong data"""
        client = ClientFactory()
        component = ComponentFactory(name="Component update validate test")
        route = reverse_lazy('order:update', kwargs={'pk': self.order.id})
        self._test_order_with_errors(route)
        self._test_order_without_errors(route, client)
        self._test_order_item_with_errors(route, client)
        self._test_order_item_without_errors(route, client, component)

    def test_update_form_save_data(self):
        data = {
            'orders-TOTAL_FORMS': 1,
            'orders-INITIAL_FORMS': 0,
            'orders-MIN_NUM_FORMS': 0,
            'orders-MAX_NUM_FORMS': 100,
            'client': self.order.client.id,
            'delivery_date': '2016-12-22',
            'status': 'O',
            'orders-0-id': self.order.orders.first().id,
            'orders-0-component_group': 'main_dish',
            'orders-0-price': '5',
            'orders-0-billable_flag': True,
            'orders-0-size': 'R',
            'orders-0-order_item_type': 'meal_component',
            'orders-0-remark': 'Order item without errors',
            'orders-0-total_quantity': '5',
        }
        self.client.post(
            reverse_lazy('order:update', kwargs={'pk': self.order.id}),
            data,
            follow=True
        )
        order = Order.objects.get(id=self.order.id)
        self.assertEqual(order.creation_date, date.today())
        self.assertEqual(order.delivery_date, date(2016, 12, 22))
        self.assertEqual(order.orders.latest('id').price, 5)
        self.assertEqual(order.orders.latest('id').billable_flag, True)
        self.assertEqual(order.orders.latest('id').size, 'R')
        self.assertEqual(
            order.orders.latest('id').order_item_type,
            'meal_component'
        )
        self.assertEqual(
            order.orders.latest('id').remark,
            'Order item without errors'
        )
        self.assertEqual(order.orders.latest('id').total_quantity, 5)


class DeleteOrderTestCase(OrderFormTestCase):

    def test_confirm_delete_order(self):
        response = self.client.get(
            reverse('order:delete', args=(self.order.id,)),
            follow=True
        )
        self.assertContains(response, 'Delete Order #{}'.format(self.order.id))

    def test_anonymous_user_gets_redirected_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('order:delete',
                                           args={self.order.id}))
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=' + reverse('order:delete',
                                                       args={self.order.id}),
            status_code=302
        )

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
