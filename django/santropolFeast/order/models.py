from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

ORDER_STATUS_CHOICES = (
	('Ordered', 1),
	('Delivered', 2),
	('Not delivered', 3),
	('Paid', 4),
)

ORDERITEM_TYPE_CHOICES = (
        ('Half', 1),
        ('Regular', 2),
        ('Double', 3),
)

class Order(models.Model):
	class Meta:
		verbose_name_plural = _('Orders')

	# Order information
	order_date = models.DateField(verbose_name=_('Date'))
	type = models.CharField(choices=ORDER_STATUS_CHOICES, verbose_name=_('Order status'))
	value = models.CharField(max_length=20, verbose_name=_('Value'))
	client = models.ForeignKey(Client, verbose_name=_('Client'))
	order_items = models.ManyToManyField(OrderItem, related_name='order_items'))

class OrderItem(models.Model):
        class Meta:
                verbose_name_plural = _('OrderItems')

	# Items information for order
	#http://stackoverflow.com/questions/1139393/what-is-the-best-django-model-field-to-use-to-represent-a-us-dollar-amount
	#type = order type if half or double or simple

	# Foreign Key to meal to get information
	meal = models.ForeignKey(Meal, verbose_name=_('Meal'))
	price = models.DecimalField(max_digits=6, decimal_places=2)
