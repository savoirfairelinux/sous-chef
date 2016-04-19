from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

import math

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

    gender = models.CharField(
        max_length=1,
        choices=(
            ('H', 'Homme'),
            ('F', 'Femme'),
            ('U', 'Inconnu'),
        ),
        default=1
    )

    birthdate = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=timezone.now
    )

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

    def age_on_date(self, date):
        """
        Returns integer specifying person's age in years on date given.

        >>> from datetime import date
        >>> p = Member()
        >>> p.age_on_date(date(2016, 4, 19))
        85
        """
        if date < self.birthdate:
            return 0
        return math.floor((date - self.birthdate).days / 365)


class Address(models.Model):

    class Meta:
        verbose_name_plural = _('addresses')

    # Member address information
    number = models.PositiveIntegerField(
        verbose_name=_('street_number')
    )

    street = models.CharField(
        max_length=100,
        verbose_name=_('street')
    )

    # Can look like B02 so can't be an IntegerField
    apartment = models.CharField(
        max_length=10,
        verbose_name=_('apartment')
    )

    floor = models.IntegerField(
        verbose_name=_('floor')
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_('city')
    )

    # Montreal postal code look like H3E 1C2
    postal_code = models.CharField(
        max_length=6,
        verbose_name=_('postal_code')
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member')
    )


class Contact(models.Model):

    class Meta:
        verbose_name_plural = _('contacts')

    # Member contact information
    type = models.CharField(
        max_length=100,
        choices=CONTACT_TYPE_CHOICES,
        verbose_name=_('contact_type')
    )

    value = models.CharField(
        max_length=50,
        verbose_name=_('value')
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member')
    )


class Client(models.Model):

    # Characters are used to keep a backward-compatibility
    # with the previous system.
    PENDING = 'D'
    ACTIVE = 'A'
    PAUSED = 'S'
    STOPNOCONTACT = 'N'
    STOPCONTACT = 'C'
    DECEASED = 'I'

    CLIENT_STATUS = (
        (PENDING, _('pending')),
        (ACTIVE, _('active')),
        (PAUSED, _('paused')),
        (STOPNOCONTACT, _('stopnocontact')),
        (STOPCONTACT, _('stopcontact')),
        (DECEASED, _('deceased')),
    )

    class Meta:
        verbose_name_plural = _('clients')

    billing_address = models.ForeignKey(
        'member.Address',
        verbose_name=_('billing_Address')
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member')
    )

    status = models.CharField(
        max_length=1,
        choices=CLIENT_STATUS,
        default=PENDING
    )

    restrictions = models.ManyToManyField(
        'meal.Ingredient',
        related_name='restricted_clients'
    )

    allergies = models.ManyToManyField(
        'meal.Allergy',
        related_name='allergic_clients'
    )
