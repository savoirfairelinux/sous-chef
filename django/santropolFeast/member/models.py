from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django_filters import FilterSet, MethodFilter, CharFilter, ChoiceFilter
from annoying.fields import JSONField

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

RATE_TYPE = (
    ('default', _('Default')),
    ('low income', _('Low income')),
    ('solidary', _('Solidary')),
)

PAYMENT_TYPE = (
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

OPTION_GROUP_CHOICES = (
    ('main dish size', _('Main dish size')),
    ('dish', _('Dish')),
    ('preparation', _('Preparation')),
    ('other order item', _('Other order item')),
)

DAYS_OF_WEEK = (
    ('mon', _('Monday')),
    ('tue', _('Tuesday')),
    ('wed', _('Wednesday')),
    ('thu', _('Thursday')),
    ('fri', _('Friday')),
    ('sat', _('Saturday')),
    ('sun', _('Sunday')),
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

    address = models.ForeignKey(
        'member.Address',
        verbose_name=_('address'),
        null=True,
    )

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

    def get_home_phone(self):
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


class Route(models.Model):

    class Meta:
        verbose_name_plural = _('Routes')

    # Information about options added to the meal
    name = models.CharField(
        max_length=50,
        verbose_name=_('name')
    )

    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class ClientManager(models.Manager):

    def get_birthday_boys_and_girls(self):

        today = datetime.datetime.now()

        return self.filter(
            birthdate__month=today.month,
            birthdate__day=today.day
        )


class ActiveClientManager(ClientManager):

    def get_queryset(self):

        return super(ActiveClientManager, self).get_queryset().filter(
            status=Client.ACTIVE
        )


class PendingClientManager(ClientManager):

    def get_queryset(self):

        return super(PendingClientManager, self).get_queryset().filter(
            status=Client.PENDING
        )


class ContactClientManager(ClientManager):

    def get_queryset(self):

        return super(ContactClientManager, self).get_queryset().filter(
            Q(status=Client.ACTIVE) |
            Q(status=Client.STOPCONTACT) |
            Q(status=Client.PAUSED) |
            Q(status=Client.PENDING)
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

    LANGUAGES = (
        ('en', _('English')),
        ('fr', _('French')),
    )

    class Meta:
        verbose_name_plural = _('clients')

    billing_member = models.ForeignKey(
        'member.Member',
        related_name='+',
        verbose_name=_('billing member'),
    )

    billing_payment_type = models.CharField(
        verbose_name=_('Payment Type'),
        max_length=10,
        null=True,
        choices=PAYMENT_TYPE,
    )

    rate_type = models.CharField(
        verbose_name=_('rate type'),
        max_length=10,
        choices=RATE_TYPE,
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

    emergency_contact_relationship = models.CharField(
        max_length=100,
        verbose_name=_('emergency contact relationship'),
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=1,
        choices=CLIENT_STATUS,
        default=PENDING
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

    gender = models.CharField(
        max_length=1,
        default='U',
        blank=True,
        null="True",
        choices=GENDER_CHOICES,
    )

    birthdate = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=timezone.now,
        blank=True,
        null=True
    )

    route = models.ForeignKey(
        'member.Route',
        verbose_name=_('route'),
        blank=True,
        null=True
    )

    meal_default_monday = JSONField(
        blank=True, null=True
    )

    meal_default_tuesday = JSONField(
        blank=True, null=True
    )

    meal_default_wednesday = JSONField(
        blank=True, null=True
    )

    meal_default_thursday = JSONField(
        blank=True, null=True
    )

    meal_default_friday = JSONField(
        blank=True, null=True
    )

    meal_default_saturday = JSONField(
        blank=True, null=True
    )

    meal_default_sunday = JSONField(
        blank=True, null=True
    )

    def __str__(self):
        return "{} {}".format(self.member.firstname, self.member.lastname)

    objects = ClientManager()

    active = ActiveClientManager()
    pending = PendingClientManager()
    contact = ContactClientManager()

    @property
    def age(self):
        """
        Returns integer specifying person's age in years on the current date.

        >>> from datetime import date
        >>> p = Client(birthdate=date(1950, 4, 19)
        >>> p.age()
        66
        """
        from datetime import date
        current = date.today()

        if current < self.birthdate:
            return 0
        return math.floor((current - self.birthdate).days / 365)

    @property
    def orders(self):
        """
        Returns orders associated to this client
        """

        return self.client_order.all()


class ClientFilter(FilterSet):

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    status = ChoiceFilter(
        choices=(('', ''),) + Client.CLIENT_STATUS
    )

    delivery_type = ChoiceFilter(
        choices=(('', ''),) + DELIVERY_TYPE
    )

    class Meta:
        model = Client
        fields = ['route', 'status', 'delivery_type']

    def filter_search(self, queryset, value):
        if not value:
            return queryset

        name_contains = Q()
        names = value.split(' ')

        for name in names:

            firstname_contains = Q(
                member__firstname__icontains=name
            )

            lastname_contains = Q(
                member__lastname__icontains=name
            )

            name_contains |= firstname_contains | lastname_contains

        return queryset.filter(name_contains)


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


class Option(models.Model):

    class Meta:
        verbose_name_plural = _('options')

    # Information about options added to the meal
    name = models.CharField(
        max_length=50,
        verbose_name=_('name')
    )

    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )

    option_group = models.CharField(
        max_length=100,
        choices=OPTION_GROUP_CHOICES,
        verbose_name=_('option group')
    )

    def __str__(self):
        return self.name


class Client_option(models.Model):
    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='+')

    option = models.ForeignKey(
        'member.option',
        verbose_name=_('option'),
        related_name='+')

    value = models.CharField(
        max_length=100,
        null=True,
        verbose_name=_('value')
    )
    #  value contents depends on option_group of option occurence pointed to:
    #    if option_group = main_dish_size : 'Regular' or 'Large'
    #    if option_group = dish : qty Monday to Sunday ex. '1110120'
    #    if option_group = preparation : Null
    #    if option_group = other_order_item : No occurrence of Client_option

    def __str__(self):
        return "{} {} <has> {}".format(self.client.member.firstname,
                                       self.client.member.lastname,
                                       self.option.name)


class Restriction(models.Model):
    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='+')

    restricted_item = models.ForeignKey(
        'meal.Restricted_item',
        verbose_name=_('restricted item'),
        related_name='+')

    def __str__(self):
        return "{} {} <restricts> {}".format(self.client.member.firstname,
                                             self.client.member.lastname,
                                             self.restricted_item.name)


class Client_avoid_ingredient(models.Model):
    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='+')

    ingredient = models.ForeignKey(
        'meal.Ingredient',
        verbose_name=_('ingredient'),
        related_name='+')

    def __str__(self):
        return "{} {} <has> {}".format(self.client.member.firstname,
                                       self.client.member.lastname,
                                       self.ingredient.name)


class Client_avoid_component(models.Model):
    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='+')

    component = models.ForeignKey(
        'meal.Component',
        verbose_name=_('component'),
        related_name='+')

    def __str__(self):
        return "{} {} <has> {}".format(self.client.member.firstname,
                                       self.client.member.lastname,
                                       self.component.name)
