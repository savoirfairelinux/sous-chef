from django.db import models
from django.utils.translation import ugettext_lazy as _

ORDER_STATUS_CHOICES = (
    (_('Ordered'), 1),
    (_('Delivered'), 2),
    (_('No charge'), 3),
    (_('Paid'), 4),
)

ORDERITEM_TYPE_CHOICES = (
    (_('Half'), 1),
    (_('Regular'), 2),
    (_('Double'), 3),
)


class Order(models.Model):

    class Meta:
        verbose_name_plural = _('orders')

    # Order information
    creation_date = models.DateField(
        verbose_name=_('date')
    )

    type = models.CharField(
        max_length=100,
        choices=ORDER_STATUS_CHOICES,
        verbose_name=_('order status')
    )

    value = models.CharField(
        max_length=20,
        verbose_name=_('value')
    )

    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client')
    )

    order_items = models.ManyToManyField(
        'order.OrderItem',
        related_name='order_items'
    )


class OrderItem(models.Model):

    class Meta:
        verbose_name_plural = _('order items')

    # Foreign Key to meal to get information
    meal = models.ForeignKey(
        'meal.Meal',
        verbose_name=_('meal')
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('price')
    )
