from django.db.models.signals import post_delete
from django.dispatch import receiver

from ..models import ClientScheduledStatus


@receiver(
    post_delete,
    sender=ClientScheduledStatus,
    dispatch_uid="post_delete.ensure_pair_remove"
)
def ensure_pair_remove(sender, instance, **kwargs):
    if instance.get_pair:
        ClientScheduledStatus.objects.get(pk=instance.get_pair.pk).delete()
