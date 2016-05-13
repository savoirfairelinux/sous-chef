from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class Notification(models.Model):

    PRIORITY_LEVEL_NORMAL = 'normal'
    PRIORITY_LEVEL_URGENT = 'urgent'

    PRIORITY_LEVEL = (
        (PRIORITY_LEVEL_NORMAL, _('Normal')),
        (PRIORITY_LEVEL_URGENT, _('Urgent')),
    )

    class Meta:
        verbose_name_plural = _('Notifications')

    description = models.TextField(
        verbose_name=_('Description')
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('Member')
    )

    priority = models.CharField(
        max_length=15,
        choices=PRIORITY_LEVEL,
        default=PRIORITY_LEVEL_NORMAL
    )

    date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=timezone.now
    )

    def __str__(self):
        return self.description
