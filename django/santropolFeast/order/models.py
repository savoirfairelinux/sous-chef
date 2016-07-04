from django.db import models
from django.db.models import Q
from member.models import Client, Member
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, MethodFilter
import re

ORDER_STATUS_CHOICES = (
    ('O', _('Ordered')),
    ('D', _('Delivered')),
    ('B', _('Billed')),
    ('P', _('Paid')),
)

SIZE_CHOICES = (
    ('', _('Serving size')),
    ('R', _('Regular')),
    ('L', _('Large')),
)

ORDER_ITEM_TYPE_CHOICES = (
    ('', _('Order item type')),
    ('B component',
     _('BILLABLE meal component (main dish, vegetable, side dish, seasonal)')),
    ('B delivery',
     _('BILLABLE delivery (general store item, ...)')),
    ('N delivery',
     _('NON BILLABLE delivery (ex. invitation card, ...)')),
    ('N pickup',
     _('NON BILLABLE pickup (payment)')),
)


class OrderManager(models.Manager):

    def get_orders_for_date(self, delivery_date=None):
        """ Return the orders for the given date """

        return self.get_queryset().filter(
           delivery_date=delivery_date
        )


class Order(models.Model):

    class Meta:
        verbose_name_plural = _('orders')

    # Order information
    creation_date = models.DateField(
        verbose_name=_('creation date')
    )

    delivery_date = models.DateField(
        verbose_name=_('delivery date')
    )

    status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS_CHOICES,
        verbose_name=_('order status')
    )

    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='client_order',
    )

    objects = OrderManager()

    @property
    def price(self):

        total = 0

        for item in self.orders.all():

            if item.billable_flag is True:

                total = total + item.price

        return total

    def __str__(self):
        return "client={}, delivery_date={}".format(
            self.client,
            self.delivery_date
        )


class OrderFilter(FilterSet):

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    class Meta:
        model = Order
        fields = ['status']

    def filter_search(self, queryset, value):
        if not value:
            return queryset

        names = value.split(' ')

        name_contains = Q()

        for name in names:
            firstname_contains = Q(
                client__member__firstname__icontains=name
            )

            name_contains |= firstname_contains

            lastname_contains = Q(
                client__member__lastname__icontains=name
            )
            name_contains |= lastname_contains

        return queryset.filter(
            name_contains
        )


class Order_item(models.Model):

    class Meta:
        verbose_name_plural = _('order items')

    order = models.ForeignKey(
        'order.Order',
        verbose_name=_('order'),
        related_name='orders',
    )

    component = models.ForeignKey(
        'meal.Component',
        verbose_name=_('component'),
        null=True,
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('price')
    )

    billable_flag = models.BooleanField(
        verbose_name=_('billable flag'),
    )

    size = models.CharField(
        verbose_name=_('size'),
        max_length=1,
        null=True,
        choices=SIZE_CHOICES,
    )

    order_item_type = models.CharField(
        verbose_name=_('order item type'),
        max_length=20,
        choices=ORDER_ITEM_TYPE_CHOICES,
    )

    remark = models.CharField(
        max_length=256,
        verbose_name=_('remark')
    )

    total_quantity = models.IntegerField(
        verbose_name=_('total quantity'),
        null=True,
    )

    free_quantity = models.IntegerField(
        verbose_name=_('free quantity'),
        null=True,
    )
