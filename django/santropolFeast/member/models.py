from django.db import models
from django.utils.translation import ugettext_lazy as _

CONTACT_TYPE_CHOICES = (
    ('Home phone', 1),
    ('Cell phone', 2),
    ('Work phone', 3),
    ('Email', 4),
)


class Member(models.Model):

    class Meta:
        verbose_name_plural = _('members')

        # Member information
        firstname = models.CharField(
            max_length=50,
            verbose_name=_('firstname')
        )

        lastname = models.CharField(
            max_length=50,
            verbose_name=_('lastname')
        )


class Address(models.Model):

    class Meta:
        verbose_name_plural = _('addresses')

    # Member address information
    number = models.CharField(
        max_length=50,
        verbose_name=_('street_number')
    )

    street = models.CharField(
        max_length=100,
        verbose_name=_('street')
    )

    apartment = models.CharField(
        max_length=10,
        verbose_name=_('apartment')
    )

    floor = models.CharField(
        max_length=3,
        verbose_name=_('floor')
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_('city')
    )

    postal_code = models.CharField(
        max_length=6,
        verbose_name=_('postal_code')
    )

    member = models.ForeignKey(
        'Member',
        verbose_name=_('member')
    )


class Contact(models.Model):

    class Meta:
        verbose_name_plural = _('contacts')

    # Member contact information
    type = models.CharField(
        choices=CONTACT_TYPE_CHOICES,
        verbose_name=_('contact_type')
    )
    value = models.CharField(
        max_length=50,
        verbose_name=_('value')
    )
    member = models.ForeignKey(
        'Member',
        verbose_name=_('member')
    )


class Client(models.Model):

    class Meta:
        verbose_name_plural = _('clients')

        # Client information

    billing_address = models.ForeignKey(
        'Address',
        verbose_name=_('billing_address')
    )
    member = models.ForeignKey(
        'Member',
        verbose_name=_('member')
    )
    restrictions = models.ManyToManyField(
        'Ingredient',
        related_name='restricted_clients'
    )
    allergies = models.ManyToManyField(
        'Allergy',
        related_name='allergic_clients'
    )
