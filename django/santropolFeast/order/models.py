from django.db import models
from django.utils.translation import ugettext_lazy as _

ORDER_STATUS_CHOICES = (
    ('', _('Order status')),
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
        verbose_name=_('client')
    )

    @property
    def total(self):

        total = 0

        for item in self.orders.all():

            if item.billable_flag is True:

                total = total + item.price

        return total


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
