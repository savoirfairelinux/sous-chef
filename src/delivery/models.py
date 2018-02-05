from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class Delivery(models.Model):

    class Meta:
        verbose_name_plural = _('deliveries')

    pass
