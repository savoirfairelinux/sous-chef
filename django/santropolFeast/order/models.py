from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

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
	order_date = models.DateField(verbose_name=_('date'))
	type = models.CharField(choices=ORDER_STATUS_CHOICES, verbose_name=_('order_status'))
	value = models.CharField(max_length=20, verbose_name=_('value'))
	client = models.ForeignKey(Client, verbose_name=_('client'))
	order_items = models.ManyToManyField(OrderItem, related_name='order_items'))


class OrderItem(models.Model):
        class Meta:
                verbose_name_plural = _('order_items')

	# Items information for order
	#http://stackoverflow.com/questions/1139393/what-is-the-best-django-model-field-to-use-to-represent-a-us-dollar-amount
	#type = order type if half or double or simple

	# Foreign Key to meal to get information
	meal = models.ForeignKey(Meal, verbose_name=_('meal'))
	price = models.DecimalField(max_digits=6, decimal_places=2)
