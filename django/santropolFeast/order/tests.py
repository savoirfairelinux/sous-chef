from django.test import TestCase
from member.models import Client, Address, Member
from order.models import Order, Order_item
from order.factories import OrderFactory
from member.factories import RouteFactory
from datetime import date, datetime
from django.contrib.auth.models import User


class OrderTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        RouteFactory.create_batch(10)

    def test_get_orders_for_Date(self):

        order = OrderFactory()

        self.assertTrue(
            len(
                Order.objects.get_orders_for_date(
                    delivery_date=date.today()
                )
            ) == 1
        )


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
        zero_order_item = Order_item.objects.create(order=total_zero_order,
                                                    price=22.50,
                                                    billable_flag=False,
                                                    order_item_type="",
                                                    remark="12")

        order = Order.objects.create(
            creation_date=date(2016, 5, 5),
            delivery_date=date(2016, 5, 10),
            status='B', client=client,
        )

        billable_order_item = Order_item.objects.create(
            order=order, price=6.50, billable_flag=True, order_item_type="",
            remark="testing", size="R",
        )

        non_billable_order_item = Order_item.objects.create(
            order=order, price=12.50, billable_flag=False, order_item_type="",
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
