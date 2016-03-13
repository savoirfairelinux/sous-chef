from django.db import models
from django.utils.translation import ugettext_lazy as _

ORDER_STATUS_CHOICES = (
    (_('ordered'), 1),
    (_('delivered'), 2),
    (_('no_charge'), 3),
    (_('paid'), 4),
)

ORDERITEM_TYPE_CHOICES = (
    (_('half'), 1),
    (_('regular'), 2),
    (_('double'), 3),
)


class Order(models.Model):

    class Meta:
        verbose_name_plural = _('orders')

    # Order information
    order_date = models.DateField(
        verbose_name=_('date')
    )

    type = models.CharField(
        max_length=100,
        choices=ORDER_STATUS_CHOICES,
        verbose_name=_('order_status')
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
        verbose_name_plural = _('order_items')

    # Foreign Key to meal to get information
    meal = models.ForeignKey(
        'meal.Meal',
        verbose_name=_('meal')
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )
