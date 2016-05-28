from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django_filters import FilterSet, MethodFilter
import datetime
import re

import math

HOME = 'Home phone'
CELL = 'Cell phone'
WORK = 'Work phone'
EMAIL = 'Email'

GENDER_CHOICES = (
    ('', _('Gender')),
    ('F', _('Female')),
    ('M', _('Male')),
)

CONTACT_TYPE_CHOICES = (
    (HOME, HOME),
    (CELL, CELL),
    (WORK, WORK),
    (EMAIL, EMAIL),
)

FACTURATION_TYPE = (
    ('default', _('Default')),
    ('low income', _('Low income')),
    ('solidary', _('Solidary')),
)

PAYMENT_TYPE = (
    ('', _('Payment type')),
    ('check', _('Check')),
    ('cash', _('Cash')),
    ('debit', _('Debit card')),
    ('credit', _('Credit card')),
    ('eft', _('EFT')),
)

DELIVERY_TYPE = (
    ('O', _('Ongoing')),
    ('E', _('Episodic')),
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
        verbose_name=_('street number'),
        blank=True,
        null=True,
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
        verbose_name=_('member'),
        related_name=('member_address')
    )

    def __str__(self):
        return self.street


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
        related_name='member_contact',
    )

    def __str__(self):
        return "{} {}".format(self.member.firstname, self.member.lastname)


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

    LANGUAGES = (
        ('en', _('English')),
        ('fr', _('French')),
    )

    class Meta:
        verbose_name_plural = _('clients')

    billing_address = models.ForeignKey(
        'member.Address',
        verbose_name=_('billing address')
    )

    billing_payment_type = models.CharField(
        verbose_name=_('Payment Type'),
        max_length=10,
        null=True,
        choices=PAYMENT_TYPE,
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

    language = models.CharField(
        max_length=2,
        choices=LANGUAGES,
        default='fr'
    )

    alert = models.TextField(
        verbose_name=_('alert client'),
        blank=True,
        null=True,
    )

    delivery_type = models.CharField(
        max_length=1,
        choices=DELIVERY_TYPE,
        default='O'
    )

    def __str__(self):
        return "{} {}".format(self.member.firstname, self.member.lastname)


class ClientFilter(FilterSet):

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    class Meta:
        model = Client

    def filter_search(self, queryset, value):
        if value:
            query = []

            value = re.sub('[^\w]', '', value).split()

            for word in value:

                firstname = list(
                    queryset.filter(
                        member__firstname__icontains=word
                    ).all()
                )

                lastname = list(
                    queryset.filter(
                        member__lastname__icontains=word
                    ).all()
                )
                for user in firstname:
                    if user not in query:
                        query.append(user)

                for user in lastname:
                    if user not in query:
                        query.append(user)

                return query

        else:
            return queryset


class Referencing (models.Model):

    class Meta:
        verbose_name_plural = _('referents')

    referent = models.ForeignKey('member.Member',
                                 verbose_name=_('referent'))

    client = models.ForeignKey('member.Client',
                               verbose_name=_('client'),
                               related_name='client_referent')

    referral_reason = models.TextField(
        verbose_name=_("Referral reason")
    )

    work_information = models.TextField(
        verbose_name=_('Work information'),
        blank=True,
        null=True,
    )

    date = models.DateField(verbose_name=_("Referral date"),
                            auto_now=False, auto_now_add=False,
                            default=datetime.date.today)

    def __str__(self):
        return "{} {} referred {} {} on {}".format(
            self.referent.firstname, self.referent.lastname,
            self.client.member.firstname, self.client.member.lastname,
            str(self.date))


class Note (models.Model):

    PRIORITY_LEVEL_NORMAL = 'normal'
    PRIORITY_LEVEL_URGENT = 'urgent'

    PRIORITY_LEVEL = (
        (PRIORITY_LEVEL_NORMAL, _('Normal')),
        (PRIORITY_LEVEL_URGENT, _('Urgent')),
    )

    class Meta:
        verbose_name_plural = _('Notes')

    note = models.TextField(
        verbose_name=_('Note')
    )

    author = models.ForeignKey(
        User,
        verbose_name=_('Author'),
        related_name='Notes'
    )

    date = models.DateField(
        verbose_name=_('Date'),
        default=timezone.now,
    )

    is_read = models.BooleanField(
        verbose_name=_('Is read'),
        default=False
    )

    member = models.ForeignKey(
        'member.Member',
        verbose_name=_('Member'),
        related_name='Notes'
    )

    priority = models.CharField(
        max_length=15,
        choices=PRIORITY_LEVEL,
        default=PRIORITY_LEVEL_NORMAL
    )

    def __str__(self):
        return self.note

    def mark_as_read(self):
        """Mark a note as read."""
        if not self.is_read:
            self.is_read = True
            self.save()
