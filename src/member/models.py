import datetime
import math
import json
from member.formsfield import CAPhoneNumberExtField
from django.forms import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import User
from django_filters import (
    FilterSet, MethodFilter, CharFilter, ChoiceFilter, BooleanFilter
)
from annoying.fields import JSONField
from meal.models import (
    COMPONENT_GROUP_CHOICES, COMPONENT_GROUP_CHOICES_MAIN_DISH
)
from note.models import Note


HOME = 'Home phone'
CELL = 'Cell phone'
WORK = 'Work phone'
EMAIL = 'Email'

GENDER_CHOICES = (
    ('F', _('Female')),
    ('M', _('Male')),
    ('O', _('Other')),
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

RATE_TYPE_LOW_INCOME = RATE_TYPE[1][0]
RATE_TYPE_SOLIDARY = RATE_TYPE[2][0]

PAYMENT_TYPE = (
    ('cheque', _('Cheque')),
    ('cash', _('Cash')),
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

OPTION_GROUP_CHOICES_PREPARATION = OPTION_GROUP_CHOICES[2][0]

DAYS_OF_WEEK = (
    ('monday', _('Monday')),
    ('tuesday', _('Tuesday')),
    ('wednesday', _('Wednesday')),
    ('thursday', _('Thursday')),
    ('friday', _('Friday')),
    ('saturday', _('Saturday')),
    ('sunday', _('Sunday')),
)


class Member(models.Model):

    class Meta:
        verbose_name_plural = _('members')

    mid = models.IntegerField(
        null=True
    )

    rid = models.IntegerField(
        null=True
    )

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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return "{} {}".format(self.firstname, self.lastname)

    @property
    def home_phone(self):
        try:
            val_orig = self.member_contact.filter(type=HOME).first().value
            f = CAPhoneNumberExtField()
            val_clean = f.clean(val_orig)
            if val_orig != val_clean:
                self.member_contact.filter(type=HOME).first().value = val_clean
                self.add_contact_information(HOME, val_clean, True)
                return val_clean
            return val_orig
        except ValidationError as error:
            return self.member_contact.filter(type=HOME).first().value
        except:
            return ""

    @property
    def cell_phone(self):
        try:
            val_orig = self.member_contact.filter(type=CELL).first().value
            f = CAPhoneNumberExtField()
            val_clean = f.clean(val_orig)
            if val_orig != val_clean:
                self.member_contact.filter(type=CELL).first().value = val_clean
                self.add_contact_information(CELL, val_clean, True)
                return val_clean
            return val_orig
        except ValidationError as error:
            return self.member_contact.filter(type=CELL).first().value
        except:
            return ""

    @property
    def work_phone(self):
        try:
            val_orig = self.member_contact.filter(type=WORK).first().value
            f = CAPhoneNumberExtField()
            val_clean = f.clean(val_orig)
            if val_orig != val_clean:
                self.member_contact.filter(type=WORK).first().value = val_clean
                self.add_contact_information(WORK, val_clean, True)
                return val_clean
            return val_orig
        except ValidationError as error:
            return self.member_contact.filter(type=WORK).first().value
        except:
            return ""

    @property
    def email(self):
        try:
            return self.member_contact.all().filter(type=EMAIL).first().value
        except:
            return ""

    def add_contact_information(self, type, value, force_update=False):
        """
        Attach a new contact information to the member instance.
        If a contact information of the given type already exists, it should be
        updated. Otherwise, it should create a new one.
        """
        created = False
        if value is None:
            value = ''

        if force_update or value is not '':
            contact, created = Contact.objects.update_or_create(
                member=self, type=type,
                defaults={
                    'value': value,
                    'member': self
                }
            )
        return created


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
        max_length=7,
        verbose_name=_('postal code')
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )

    distance = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
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

    def display_value(self):
        if self.type in (HOME, WORK, CELL):
            try:
                f = CAPhoneNumberExtField()
                return f.clean(self.value)
            except ValidationError as error:
                return self.value
            except:
                return ""
        return self.value

    def __str__(self):
        return "{} {}".format(self.member.firstname, self.member.lastname)


class Route(models.Model):

    class Meta:
        verbose_name_plural = _('Routes')
        ordering = ['name']

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

    # ordered client ids for the current delivery
    #   saved by Organize Routes sequencing page
    client_id_sequence = JSONField(
        blank=True, null=True
    )

    def __str__(self):
        return self.name

    def set_client_sequence(self, date, route_client_ids):
        # save sequence of points for a delivery route
        self.client_id_sequence = {date.strftime('%Y-%m-%d'): route_client_ids}

    def get_client_sequence(self):
        # retrieve sequence of points for a delivery route
        if self.client_id_sequence:
            # ['date on which sequence was stored', [client_id, ...]]
            return list(self.client_id_sequence.items())[0]
        else:
            return (None, None)


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


class OngoingClientManager(ClientManager):

    def get_queryset(self):

        return super(OngoingClientManager, self).get_queryset().filter(
            status=Client.ACTIVE, delivery_type='O'
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
        ('al', _('Allophone')),
    )

    class Meta:
        verbose_name_plural = _('clients')
        ordering = ["-member__created_at"]

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

    meal_default_week = JSONField(
        blank=True, null=True
    )

    delivery_note = models.TextField(
        verbose_name=_('Delivery Note'),
        blank=True,
        null=True
    )

    ingredients_to_avoid = models.ManyToManyField(
        'meal.Ingredient',
        through='Client_avoid_ingredient'
    )

    components_to_avoid = models.ManyToManyField(
        'meal.Component',
        through='Client_avoid_component'
    )

    options = models.ManyToManyField(
        'member.option',
        through='Client_option'
    )

    restrictions = models.ManyToManyField(
        'meal.Restricted_item',
        through='Restriction'
    )

    def __str__(self):
        return "{} {}".format(self.member.firstname, self.member.lastname)

    objects = ClientManager()

    active = ActiveClientManager()
    pending = PendingClientManager()
    ongoing = OngoingClientManager()
    contact = ContactClientManager()

    @property
    def is_geolocalized(self):
        """
        Returns if the client's address is properly geolocalized.
        """
        if self.member.address.latitude is None or \
                self.member.address.longitude is None:
            return False
        return True

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

    @property
    def food_preparation(self):
        """
        Returns specific food preparation associated to this client
        """
        return self.options.filter(option_group='preparation')

    @property
    def notes(self):
        """
        Returns notes associated to this client
        """
        return self.client_notes.all()

    @property
    def simple_meals_schedule(self):
        """
        Returns a list of days, corresponding to the client's delivery
        days.
        """
        option = Option.objects.get(name='meals_schedule')
        try:
            meals_schedule_option = Client_option.objects.get(
                client=self, option=option
            )
            return json.loads(meals_schedule_option.value)
        except Client_option.DoesNotExist:
            return None

    @property
    def meals_default(self):
        """
        Returns a list of tuple ((weekday, meal default), ...).

        Consider a meal default "not properly configured" if:
        (1) if all numeric fields are 0;
        (2) OR any numeric field is None;
        (2) OR if size is None
        and thus set it to None.

        Intended to be used for Episodic clients.
        """
        defaults = []
        for day, str in DAYS_OF_WEEK:
            current = {}
            numeric_fields = []
            for component, label in COMPONENT_GROUP_CHOICES:
                item = self.meal_default_week.get(
                    component + '_' + day + '_quantity'
                )
                current[component] = item
                numeric_fields.append(item)

            size = self.meal_default_week.get(
                'size_' + day
            )
            current['size'] = size

            not_properly_configured = (
                all(map(lambda x: x == 0, numeric_fields)) or
                any(map(lambda x: x is None, numeric_fields)) or
                size is None
            )
            if not_properly_configured:
                current = None
            defaults.append((day, current))

        return defaults

    @property
    def meals_schedule(self):
        """
        Returns a list of tuple ((weekday, meal default), ...).

        Intended to be used for Ongoing clients.
        """
        defaults = self.meals_default
        prefs = []
        for day, meal_schedule in defaults:
            if day not in self.simple_meals_schedule:
                prefs.append((day, None))
            else:
                prefs.append((day, meal_schedule))
        return prefs

    def set_meals_schedule(self, schedule):
        """
        Set the delivery days for the client.
        @param schedule
            A python list of days.
        """
        id = None
        try:
            option, created = Option.objects.get_or_create(
                name='meals_schedule')
            meals_schedule_option = Client_option.objects.get(
                client=self, option=option
            )
            id = meals_schedule_option.id
        except Client_option.DoesNotExist:
            pass

        option, created = Client_option.objects.update_or_create(
            id=id,
            defaults={
                'client': self,
                'option': option,
                'value': json.dumps(schedule),
            }
        )

    @staticmethod
    def get_meal_defaults(client, component_group, day):
        """Get the meal defaults quantity and size for a day.

        # TODO fix keys in wizard code to use Component_group constants

        Static method called only on class object.

        Parameters:
          client : client objectget_meal_defaults
          component_group : as in meal.models.COMPONENT_GROUP_CHOICES
          day : day of week where 0 is monday, 6 is sunday

        Returns:
          (quantity, size)

        Prerequisite:
          client.meal_default_week is a dictionary like
            {
              "compote_friday_quantity": null,
              ...
              "compote_wednesday_quantity": null,
              "dessert_friday_quantity": 2,
              ...
              "dessert_wednesday_quantity": null,
              "diabetic_friday_quantity": null,
              ...
              "fruit_salad_friday_quantity": null,
              "green_salad_friday_quantity": 2,
              "main_dish_friday_quantity": 2,
              "main_dish_wednesday_quantity": 1,
              "pudding_friday_quantity": null,
              "pudding_wednesday_quantity": null,
              "size_friday": "R",
              ...
              "size_saturday": "",
            }
        """

        meals_default = client.meal_default_week
        if meals_default:
            quantity = meals_default.get(
                component_group + '_' + DAYS_OF_WEEK[day][0] + '_quantity'
            ) or 0
            size = meals_default.get('size_' + DAYS_OF_WEEK[day][0]) or ''
        else:
            quantity = 0
            size = ''
        # DEBUG
        # print("client, compgroup, day, qty, size",
        #       client, component_group, DAYS_OF_WEEK[day][0], quantity, size)
        return quantity, size

    def set_meal_defaults(self, component_group, day, quantity=0, size=''):
        """Set the meal defaults quantity and size for a day.

        Static method called only on class object.

        Parameters:
          component_group : as in meal.models.COMPONENT_GROUP_CHOICES
          day : day of week where 0 is monday, 6 is sunday
          quantity : number of servings of this component_group
          size : size of the serving of this component_group
        """

        if not self.meal_default_week:
            self.meal_default_week = {}
        self.meal_default_week[
            component_group + '_' + DAYS_OF_WEEK[day][0] + '_quantity'
        ] = quantity
        if component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH:
            self.meal_default_week['size_' + DAYS_OF_WEEK[day][0]] = size
        # DEBUG
        # print("SET client, compgroup, day, qty, size, dict",
        #       self, component_group, days[day], quantity, size,
        #       self.meal_default_week)

    def get_meals_prefs(self):
        """
        Returns a list of items defined per client.
        """
        try:
            option, created = Option.objects.get_or_create(
                name='meals_default')
            meals_prefs_opt = Client_option.objects.get(
                client=self, option=option
            )
            return json.loads(meals_prefs_opt.value)
        except Client_option.DoesNotExist:
            return {}

    def set_meals_prefs(self, data):
        if (data['delivery_type'] == 'E'):
            option, created = Option.objects.get_or_create(
                name='meals_default')
            prefs = {
                "maindish_q": data['main_dish_default_quantity'],
                "maindish_s": data['size_default'],
                "dst_q": data['dessert_default_quantity'],
                "diabdst_q": data['diabetic_default_quantity'],
                "fruitsld_q": data['fruit_salad_default_quantity'],
                "greensld_q": data['green_salad_default_quantity'],
                "pudding_q": data['pudding_default_quantity'],
                "compot_q": data['compote_default_quantity'],
            }
            Client_option.objects.update_or_create(
                client=self, option=option,
                defaults={
                    'value': json.dumps(prefs),
                })


class ClientScheduledStatus(models.Model):

    START = 'START'
    END = 'END'

    CHANGE_STATUS = (
        (START, _('Start')),
        (END, _('End')),
    )

    TOBEPROCESSED = 'NEW'
    PROCESSED = 'PRO'
    ERROR = 'ERR'

    OPERATION_STATUS = (
        (TOBEPROCESSED, _('To be processed')),
        (PROCESSED, _('Processed')),
        (ERROR, _('Error')),
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='scheduled_statuses'
    )

    linked_scheduled_status = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )

    status_from = models.CharField(
        max_length=1,
        choices=Client.CLIENT_STATUS
    )

    status_to = models.CharField(
        max_length=1,
        choices=Client.CLIENT_STATUS
    )

    reason = models.CharField(
        max_length=200,
        blank=True,
        default=''
    )

    change_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=timezone.now,
    )

    change_state = models.CharField(
        max_length=5,
        choices=CHANGE_STATUS,
        default=START
    )

    operation_status = models.CharField(
        max_length=3,
        choices=OPERATION_STATUS,
        default=TOBEPROCESSED
    )

    class Meta:
        ordering = ['change_date']

    def __str__(self):
        return "Update {} status: from {} to {}, on {}".format(
            self.client.member,
            self.get_status_from_display(),
            self.get_status_to_display(),
            self.change_date
        )

    def process(self):
        """ Process a scheduled change if valid."""
        if self.is_valid():
            # Update the client status
            self.client.status = self.status_to
            self.client.save()
            # Update the instance status
            self.operation_status = self.PROCESSED
            self.save()
            # Add note to client
            self.add_note_to_client()
            return True
        else:
            self.operation_status = self.ERROR
            self.save()
            return False

    def is_valid(self):
        """ Returns True if a scheduled change must be applied."""
        return self.client.status == self.status_from \
            and self.operation_status == self.TOBEPROCESSED

    def add_note_to_client(self, author=None):
        note = Note(
            note=self,
            author=author,
            client=self.client,
        )
        note.save()


class ClientScheduledStatusFilter(FilterSet):

    ALL = 'ALL'

    operation_status = ChoiceFilter(
        choices=((ALL, _('All')),) + ClientScheduledStatus.OPERATION_STATUS,
        # initial=ClientScheduledStatus.PROCESSED
    )

    class Meta:
        model = ClientScheduledStatus
        fields = ['operation_status']


class ClientFilter(FilterSet):

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    status = ChoiceFilter(
        choices=(('', ''),) + Client.CLIENT_STATUS,
    )

    delivery_type = ChoiceFilter(
        choices=(('', ''),) + DELIVERY_TYPE
    )

    class Meta:
        model = Client
        fields = ['route', 'status', 'delivery_type']

    @staticmethod
    def filter_search(queryset, value):
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

    date = models.DateField(
        verbose_name=_("Referral date"),
        auto_now=False, auto_now_add=False,
        default=datetime.date.today
    )

    def __str__(self):
        return "{} {} referred {} {} on {}".format(
            self.referent.firstname, self.referent.lastname,
            self.client.member.firstname, self.client.member.lastname,
            str(self.date))


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
        max_length=255,
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
