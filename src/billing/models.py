from django.db import models
from django.db.models import Q
from member.models import Client
from order.models import Order
from annoying.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, MethodFilter, DateFilter


# Create your models here.

class OrderBilling(models.Model):
    order_id = models.ForeignKey(
        "order.Order",
        related_name='client_order'
        )
    billing_id = models.ForeignKey(
        "billing.Billing",
        related_name='client_billing'
        )


class BillingManager(models.Manager):

    def get_all_billing_client(self, client):
        pass


class Billing(models.Model):
    client = models.ForeignKey(
        "member.Client",
        )

    total_amount = models.DecimalField(
        verbose_name=_('total_amount'),
        max_digits=6,
        decimal_places=2
        )

    # Month start with january is 1
    billing_month = models.IntegerField()

    billing_year = models.IntegerField()

    created_date = models.DateTimeField(
        verbose_name=None, auto_now=True
        )

    detail = JSONField()


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


class BillingSummary(models.Model):

    total_order = models.IntegerField()
    detail = JSONField()
    billing_year = models.IntegerField()
    billing_month = models.IntegerField()
    amount_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )


# get the total amount from a list of orders
def calculate_amount_total(orders):

    total = 0

    for order in orders:

        total += order.price

    return total


# get the order detail from a list of orders
def get_order_detail(self, orders):

    detail = {"meal_regular": 0, "meal_large": 0}
