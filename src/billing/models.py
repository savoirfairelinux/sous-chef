from django.db import models
from django.db.models import Q
from member.models import Client
from order.models import Order
from datetime import datetime, date
from annoying.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, MethodFilter, DateFilter


class BillingManager(models.Manager):

    def billing_create_new(self, year, month):
        """
        Create a new billing for the given period.
        A period is a month.
         """
        # Get all billable orders for the given period
        billable_orders = Order.objects.get_billable_orders(year, month)

        # Create the Billing object
        billing = Billing.objects.create(
            total_amount=calculate_amount_total(billable_orders),
            billing_month=month,
            billing_year=year,
            created=datetime.today(),
            detail={},
        )

        # Attach the orders
        for order in billable_orders:
            billing.orders.add(order)

        return billing

    def billing_get_period(self, year, month):
        """
        Check if a billing exists for a given period.
        Return None otherwise.
        """
        billing = Billing.objects.filter(
            billing_year=year,
            billing_month=month,
        )

        if billing.count() == 0:
            return None
        else:
            return billing


class Billing(models.Model):

    total_amount = models.DecimalField(
        verbose_name=_('total_amount'),
        max_digits=6,
        decimal_places=2
    )

    # Month start with january is 1
    billing_month = models.IntegerField()

    billing_year = models.IntegerField()

    created = models.DateTimeField(
        verbose_name=None, auto_now=True
    )

    detail = JSONField()

    orders = models.ManyToManyField(Order)

    objects = BillingManager()

    @property
    def billing_period(self):
        """
        Return a readable format for the billing period.
        """
        period = date(self.billing_year, self.billing_month, 1)
        return period


class BillingFilter(FilterSet):
    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    date = MethodFilter(
        action='filter_period'
    )

    class Meta:
        model = Billing

    @staticmethod
    def filter_search(queryset, value):
        if not value:
            return queryset

        name_contains = Q()
        names = value.split(' ')

        for name in names:

            firstname_contains = Q(
                client__member__firstname__icontains=name
            )

            lastname_contains = Q(
                client__member__lastname__icontains=name
            )

            name_contains |= firstname_contains | lastname_contains

        return queryset.filter(name_contains)

    @staticmethod
    def filter_period(queryset, value):
        if not value:
            return queryset

        year, month = value.split('-')
        return queryset.filter(billing_year=year, billing_month=month)


# get the total amount from a list of orders
def calculate_amount_total(orders):
    total = 0
    for order in orders:
        total += order.price
    return total


# get the order detail from a list of orders
def get_order_detail(self, orders):

    detail = {"meal_regular": 0, "meal_large": 0}
