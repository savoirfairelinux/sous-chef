from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

import math

HOME = 'Home phone'
CELL = 'Cell phone'
WORK = 'Work phone'
EMAIL = 'Email'

GENDER_CHOICES = (
    ('M', _('male')),
    ('F', _('female')),
    ('U', _('unknown')),
)

CONTACT_TYPE_CHOICES = (
    (HOME, HOME),
    (CELL, CELL),
    (WORK, WORK),
    (EMAIL, EMAIL),
)

FACTURATION_TYPE = (
    ('default', _('default')),
    ('low income', _('low_income')),
    ('solidary', _('solidary')),
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
        default='U',
        blank="True",
        null="True",
        choices=GENDER_CHOICES,
    )

    birthdate = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=timezone.now,
        blank="True",
        null="True"
    )

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

    def age_on_date(self, date):
        """
        Returns integer specifying person's age in years on date given.

        >>> from datetime import date
        >>> p = Member(birthdate=date(1950, 4, 19)
        >>> p.age_on_date(date(2016, 4, 19))
        66
        """
        if date < self.birthdate:
            return 0
        return math.floor((date - self.birthdate).days / 365)

    def get_home_phone(self):
        for c in self.member_contact.all():
            print(c.type)
        return self.member_contact.filter(type=HOME).first() or ''


class Address(models.Model):

    class Meta:
        verbose_name_plural = _('addresses')

    # Member address information
    number = models.PositiveIntegerField(
        verbose_name=_('street number')
    )

    street = models.CharField(
        max_length=100,
        verbose_name=_('street')
    )

    # Can look like B02 so can't be an IntegerField
    apartment = models.CharField(
        max_length=10,
        verbose_name=_('apartment'),
        blank=True,
        null=True,
    )

    floor = models.IntegerField(
        verbose_name=_('floor'),
        blank=True,
        null=True,
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_('city')
    )

    # Montreal postal code look like H3E 1C2
    postal_code = models.CharField(
        max_length=6,
        verbose_name=_('postal code')
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member')
    )

    def __str__(self):
        return "{} {}".format(self.number, self.street)


class Contact(models.Model):

    class Meta:
        verbose_name_plural = _('contacts')

    # Member contact information
    type = models.CharField(
        max_length=100,
        choices=CONTACT_TYPE_CHOICES,
        verbose_name=_('contact type')
    )

    value = models.CharField(
        max_length=50,
        verbose_name=_('value')
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member'),
        related_name='member_contact'
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
        (PENDING, _('Pending')),
        (ACTIVE, _('Active')),
        (PAUSED, _('Paused')),
        (STOPNOCONTACT, _('Stop: no contact')),
        (STOPCONTACT, _('Stop: contact')),
        (DECEASED, _('Deceased')),
    )

    FACTURATION_TYPE = (
        ('default', _('Default')),
        ('low income', _('Low income')),
        ('solidary', _('Solidary')),
    )

    class Meta:
        verbose_name_plural = _('clients')

    billing_address = models.ForeignKey(
        'member.Address',
        verbose_name=_('billing address')
    )

    facturation = models.CharField(
        verbose_name=_('facturation type'),
        max_length=10,
        choices=FACTURATION_TYPE,
        default='default'
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member')
    )

    emergency_contact = models.ForeignKey(
        'member.Member',
        verbose_name=_('emergency contact'),
        related_name='emergency_contact',
        null=True,
    )

    status = models.CharField(
        max_length=1,
        choices=CLIENT_STATUS,
        default=PENDING
    )

    restrictions = models.ManyToManyField(
        'meal.Ingredient',
        related_name='restricted_clients',
        blank=True
    )

    allergies = models.ManyToManyField(
        'meal.Allergy',
        related_name='allergic_clients',
        blank=True
    )

    alert = models.TextField(
        verbose_name=_('alert client'),
        blank=True
    )

    def __str__(self):
        return "{} {}".format(self.member.firstname, self.member.lastname)


class Referencing (models.Model):

    class Meta:
        verbose_name_plural = _('referents')

    referent = models.ForeignKey('member.Member',
                                 verbose_name=_('referent'))

    client = models.ForeignKey('member.Client',
                               verbose_name=_('client'))

    referral_reason = models.TextField(
        verbose_name=_("Referral reason")
    )

    date = models.DateField(verbose_name=_("Referral date"),
                            auto_now=False, auto_now_add=False,
                            default=datetime.date.today())


class Note (models.Model):

    class Meta:
        verbose_name_plural = _('notes')

    note = models.TextField(verbose_name=_('text note'))

    author = models.ForeignKey(
        User,
        verbose_name=_('author'),
        related_name='notes'
    )

    creation_date = models.DateField(
        verbose_name=_('creation date'),
        auto_now_add=True
    )

    is_read = models.BooleanField(
        verbose_name=_('is read'),
        default=False
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('member'),
        related_name='notes'
    )
