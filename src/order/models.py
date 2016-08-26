import collections

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, MethodFilter, ChoiceFilter
from django.core.urlresolvers import reverse

from datetime import date
from sqlalchemy.sql import select
from sqlalchemy import and_

from member.apps import db_sa_session, db_sa_table
from member.models import (Client, Member,
                           RATE_TYPE_LOW_INCOME, RATE_TYPE_SOLIDARY,
                           Address, Option, Client_option, Restriction,
                           Client_avoid_ingredient, Client_avoid_component)
from meal.models import (Menu, Menu_component, Component,
                         Restricted_item, Ingredient,
                         Component_ingredient, Incompatibility,
                         COMPONENT_GROUP_CHOICES,
                         COMPONENT_GROUP_CHOICES_MAIN_DISH)


ORDER_STATUS = (
    ('O', _('Ordered')),
    ('D', _('Delivered')),
    ('N', _('No Charge')),
    ('B', _('Billed')),
    ('P', _('Paid')),
)

ORDER_STATUS_ORDERED = ORDER_STATUS[0][0]

SIZE_CHOICES = (
    ('', _('Serving size')),
    ('R', _('Regular')),
    ('L', _('Large')),
)

ORDER_ITEM_TYPE_CHOICES = (
    ('', _('Order item type')),
    ('B component',
     _('BILLABLE meal component (main dish, vegetable, side dish, seasonal)')),
    ('B delivery',
     _('BILLABLE delivery (general store item, ...)')),
    ('N delivery',
     _('NON BILLABLE delivery (ex. invitation card, ...)')),
    ('N pickup',
     _('NON BILLABLE pickup (payment)')),
)

ORDER_ITEM_TYPE_CHOICES_COMPONENT = ORDER_ITEM_TYPE_CHOICES[1][0]

MAIN_PRICE_DEFAULT = 8.00  # TODO use decimal ?
SIDE_PRICE_DEFAULT = 1.00
MAIN_PRICE_LOW_INCOME = 7.00
SIDE_PRICE_LOW_INCOME = 0.75
MAIN_PRICE_SOLIDARY = 6.00
SIDE_PRICE_SOLIDARY = 0.50


class OrderManager(models.Manager):

    def get_orders_for_date(self, delivery_date=None):
        """ Return the orders for the given date """

        if delivery_date is None:
            delivery_date = date.today()

        return self.get_queryset().filter(
            delivery_date=delivery_date,
        )

    def get_orders_for_month(self, month, year):
        """ Return the orders for the given month """
        return self.filter(
            delivery_date__year=year,
            delivery_date__month=month,
        )

    def get_orders_for_month_client(self, month, year, client):
        """Return the orders for the given month and client"""

        return self.get_queryset().filter(
            delivery_date__year=year,
            delivery_date__month=month,
            client=client,
            status="D",
        )


class Order(models.Model):

    class Meta:
        verbose_name_plural = _('orders')

    # Order information
    creation_date = models.DateField(
        verbose_name=_('creation date')
    )

    delivery_date = models.DateField(
        verbose_name=_('delivery date')
    )

    status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS,
        verbose_name=_('order status')
    )

    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='client_order',
    )

    objects = OrderManager()

    def get_absolute_url(self):
        return reverse('order:view', kwargs={'pk': self.pk})

    @property
    def price(self):
        total = 0
        for item in self.orders.all():
            if item.billable_flag is True:
                total = total + item.price

        return total

    def __str__(self):
        return "client={}, delivery_date={}".format(
            self.client,
            self.delivery_date
        )

    @staticmethod
    def create_orders_on_defaults(creation_date, delivery_date, clients):
        """Create orders and order items for one or many clients.

        Parameters:
          creation_date : date on which orders are created
          delivery_date : date on which orders are to be delivered
          clients : a list of one or many client objects

        Returns:
          Number of orders created.
        """

        num_orders_created = 0
        day = delivery_date.weekday()  # Monday is 0, Sunday is 6
        for client in clients:
            # find quantity of free side dishes based on number of main dishes
            free_side_dish_qty = Client.get_meal_defaults(
                client,
                COMPONENT_GROUP_CHOICES_MAIN_DISH, day)[0]
            # print ("Side dish", free_side_dish_qty)
            if free_side_dish_qty == 0:
                continue  # No meal for client on this day
            try:
                Order.objects.get(client=client, delivery_date=delivery_date)
                # order already created, skip order items creation
                # (if want to replace, must be deleted first)
                continue
            except Order.DoesNotExist:
                order = Order(client=client,
                              creation_date=creation_date,
                              delivery_date=delivery_date,
                              status=ORDER_STATUS_ORDERED)
                order.save()
                num_orders_created += 1
            # TODO Use Parameters Model in member to store unit prices
            if client.rate_type == RATE_TYPE_LOW_INCOME:
                main_price = MAIN_PRICE_LOW_INCOME
                side_price = SIDE_PRICE_LOW_INCOME
            elif client.rate_type == RATE_TYPE_SOLIDARY:
                main_price = MAIN_PRICE_SOLIDARY
                side_price = SIDE_PRICE_SOLIDARY
            else:
                main_price = MAIN_PRICE_DEFAULT
                side_price = SIDE_PRICE_DEFAULT
            for component_group, trans in COMPONENT_GROUP_CHOICES:
                default_qty, default_size = \
                    Client.get_meal_defaults(
                        client, component_group, day)
                if default_qty > 0:
                    total_quantity = default_qty
                    free_quantity = 0
                    if (component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH):
                        unit_price = main_price
                    else:
                        unit_price = side_price
                        while free_side_dish_qty > 0 and default_qty > 0:
                            free_side_dish_qty -= 1
                            default_qty -= 1
                            free_quantity += 1
                    oi = Order_item(
                        order=order,
                        component_group=component_group,
                        price=(total_quantity - free_quantity) * unit_price,
                        billable_flag=True,
                        size=default_size,
                        order_item_type=ORDER_ITEM_TYPE_CHOICES_COMPONENT,
                        total_quantity=total_quantity,
                        free_quantity=free_quantity)
                    oi.save()

        # print("Number of orders created = ", num_orders_created) #DEBUG
        return num_orders_created

    @staticmethod
    def get_kitchen_items(delivery_date):
        # get all client meal order specifics for delivery date

        # Use SQLAlchemy Core for selects
        # identifiers pointing directly to database tables
        tcom = db_sa_table(Component)
        tmen = db_sa_table(Menu)
        tmencom = db_sa_table(Menu_component)
        tresitm = db_sa_table(Restricted_item)
        ting = db_sa_table(Ingredient)
        tinc = db_sa_table(Incompatibility)
        tcoming = db_sa_table(Component_ingredient)
        tcli = db_sa_table(Client)
        tmem = db_sa_table(Member)
        tadd = db_sa_table(Address)
        topt = db_sa_table(Option)
        tcliopt = db_sa_table(Client_option)
        tres = db_sa_table(Restriction)
        tcliavoing = db_sa_table(Client_avoid_ingredient)
        tcliavocom = db_sa_table(Client_avoid_component)
        tord = db_sa_table(Order)
        torditm = db_sa_table(Order_item)

        # Day's avoid ingredients clashes
        q_day_avo_ing = select(
            [tcli.c.id.label('cid'),
             tmem.c.firstname, tmem.c.lastname,
             tord.c.id, tord.c.delivery_date,
             tmen.c.id, tmencom.c.id.label('menucompid'),
             ting.c.name.label('ingredient'), tcom.c.name,
             torditm.c.id, torditm.c.order_id.label('oiorderid')]).\
            select_from(
                tmem.
                join(tcli, tcli.c.member_id == tmem.c.id).
                join(tord, tord.c.client_id == tcli.c.id).
                join(tmen, tmen.c.date == delivery_date).
                join(tcliavoing, tcliavoing.c.client_id == tcli.c.id).
                join(ting, ting.c.id == tcliavoing.c.ingredient_id).
                outerjoin(tcoming, and_(tcoming.c.ingredient_id == ting.c.id,
                                        tcoming.c.date == delivery_date)).
                outerjoin(tcom, tcom.c.id == tcoming.c.component_id).
                outerjoin(
                    torditm,
                    and_(torditm.c.component_group == tcom.c.component_group,
                         torditm.c.order_id == tord.c.id)).
                outerjoin(tmencom, and_(tmencom.c.component_id == tcom.c.id,
                                        tmencom.c.menu_id == tmen.c.id))).\
            where(tord.c.delivery_date == delivery_date).\
            order_by(tcli.c.id)
        print_rows(
            q_day_avo_ing,
            "\n***** Day's avoid ingredients clashes ****\nCLIENT_ID,"
            "FIRSTNAME, LASTNAME, "
            "ORDER_ID, ORDER_DELIV_DATE, "
            "MENU_ID, MENU_COMPONENT_ID, "
            "INGREDIENT_NAME, COMP_NAME, "
            "ORDER_ITEM_ID, ORDER_ITEM_ORDER_ID")

        # Day's avoid component clashes
        q_day_avo_com = select(
            [tcli.c.id.label('cid'),
             tmem.c.firstname, tmem.c.lastname,
             tord.c.id, tord.c.delivery_date,
             tmen.c.id, tmencom.c.id.label('menucompid'),
             tcom.c.name.label('component'),
             torditm.c.id, torditm.c.order_id.label('oiorderid')]).\
            select_from(
                tmem.
                join(tcli, tcli.c.member_id == tmem.c.id).
                join(tord, and_(tord.c.client_id == tcli.c.id,
                                tord.c.delivery_date == delivery_date)).
                join(tmen, tmen.c.date == delivery_date).
                join(tcliavocom, tcliavocom.c.client_id == tcli.c.id).
                join(tcom, tcom.c.id == tcliavocom.c.component_id).
                outerjoin(
                    torditm,
                    and_(torditm.c.component_group == tcom.c.component_group,
                         torditm.c.order_id == tord.c.id)).
                outerjoin(tmencom, and_(tmencom.c.component_id == tcom.c.id,
                                        tmencom.c.menu_id == tmen.c.id))).\
            where(tord.c.delivery_date == delivery_date).\
            order_by(tcli.c.id)
        print_rows(q_day_avo_com,
                   "\n***** Day's avoid component clashes ****\nCLIENT_ID,"
                   "FIRSTNAME, LASTNAME, "
                   "ORDER_ID, ORDER_DELIV_DATE, "
                   "MENU_ID, MENU_COMPONENT_ID, "
                   "COMP_NAME, "
                   "ORDER_ITEM_ID, ORDER_ITEM_ORDER_ID")

        # Day's restrictions
        q_day_res = select(
            [tcli.c.id.label('cid'),
             tmem.c.firstname, tmem.c.lastname,
             tord.c.id, tord.c.delivery_date,
             tmen.c.id, tmencom.c.id.label('menucompid'),
             tresitm.c.name.label('restricted_item'),
             ting.c.name.label('ingredient'), tcom.c.name,
             torditm.c.id, torditm.c.order_id.label('oiorderid')]).\
            select_from(
                tmem.
                join(tcli, tcli.c.member_id == tmem.c.id).
                join(tord, tord.c.client_id == tcli.c.id).
                join(tmen, tmen.c.date == delivery_date).
                join(tres, tres.c.client_id == tcli.c.id).
                join(tresitm, tresitm.c.id == tres.c.restricted_item_id).
                outerjoin(
                    tinc,
                    tinc.c.restricted_item_id == tres.c.restricted_item_id).
                outerjoin(ting, tinc.c.ingredient_id == ting.c.id).
                outerjoin(tcoming, and_(tcoming.c.ingredient_id == ting.c.id,
                                        tcoming.c.date == delivery_date)).
                outerjoin(tcom, tcoming.c.component_id == tcom.c.id).
                outerjoin(
                    torditm,
                    and_(torditm.c.component_group == tcom.c.component_group,
                         torditm.c.order_id == tord.c.id)).
                outerjoin(tmencom, and_(tmencom.c.component_id == tcom.c.id,
                                        tmencom.c.menu_id == tmen.c.id))).\
            where(tord.c.delivery_date == delivery_date).\
            order_by(tcli.c.id)
        print_rows(q_day_res,
                   "\n***** Day's restrictions ****\nCLIENT_ID,"
                   "FIRSTNAME, LASTNAME, "
                   "ORDER_ID, ORDER_DELIV_DATE, "
                   "MENU_ID, MENU_COMPONENT_ID, "
                   "RESTRICTED_ITEM, INGREDIENT_NAME, COMP_NAME, "
                   "ORDER_ITEM_ID, ORDER_ITEM_ORDER_ID")

        # Day's preparations
        q_day_pre = select(
            [tcli.c.id.label('cid'),
             tmem.c.firstname, tmem.c.lastname,
             topt.c.name.label('food_prep'),
             tord.c.id, tord.c.delivery_date]).\
            select_from(
                tmem.
                join(tcli, tcli.c.member_id == tmem.c.id).
                join(tcliopt, tcliopt.c.client_id == tcli.c.id).
                join(topt, topt.c.id == tcliopt.c.option_id).
                join(tord, tord.c.client_id == tcli.c.id)).\
            where(and_(tord.c.delivery_date == delivery_date,
                       topt.c.option_group == 'preparation')).\
            order_by(tmem.c.lastname, tmem.c.firstname)
        print_rows(q_day_pre,
                   "\n***** Day's preparations ****\nCLIENT_ID,"
                   "FIRSTNAME, LASTNAME, "
                   "FOOD_PREP, "
                   "ORDER_ID, ORDER_DELIV_DATE")

        # Day's Delivery List
        # TODO add route filter, full address, order by postal code
        q_day_del_lis = select(
            [tcli.c.id.label('cid'), tmem.c.firstname, tmem.c.lastname,
             tadd.c.street, tadd.c.postal_code,
             torditm.c.total_quantity, torditm.c.size,
             tmen.c.id, tmencom.c.id,
             tcom.c.id.label('component_id'),
             tcom.c.component_group,
             tcom.c.name.label('component_name')]).\
            select_from(
                tmem.
                join(tcli, tcli.c.member_id == tmem.c.id).
                join(tadd, tadd.c.id == tmem.c.address_id).
                join(tmen, tmen.c.date == delivery_date).
                join(tord, tord.c.client_id == tcli.c.id).
                join(torditm, torditm.c.order_id == tord.c.id).
                join(tmencom, tmencom.c.menu_id == tmen.c.id).
                join(
                    tcom,
                    and_(tcom.c.id == tmencom.c.component_id,
                         tcom.c.component_group ==
                         torditm.c.component_group))).\
            where(tord.c.delivery_date == delivery_date).\
            order_by(tadd.c.postal_code, tmem.c.lastname, tmem.c.firstname)
        print_rows(q_day_del_lis,
                   "\n***** Delivery List ******\n CLIENT_ID,"
                   " FIRSTNAME, LASTNAME, "
                   "STREET, POSTAL_CODE, "
                   "OI_TOTAL_QUANTITY, OI_SIZE, "
                   "MENU_ID, MENU_COMPONENT_ID, "
                   "COMPONENT_ID, COMPONENT_GROUP, COMPONENT_NAME")

        kitchen_list = {}
        rows = db_sa_session.execute(q_day_avo_ing)
        for row in rows:
            check_for_new_client(kitchen_list, row)
            if row.oiorderid and row.menucompid:
                # found avoid ingredient clash
                # should be a sorted set (or ordered dict ?)
                kitchen_list[row.cid].incompatible_ingredients.append(
                    row.ingredient)
            # we Know that it is not incommpatible
            elif (row.ingredient not in
                  kitchen_list[row.cid].incompatible_ingredients):
                # found new other avoid ingredient that does not clash today
                # should be a set
                kitchen_list[row.cid].other_ingredients.append(
                    row.ingredient)
        # END FOR

        rows = db_sa_session.execute(q_day_avo_com)
        for row in rows:
            check_for_new_client(kitchen_list, row)
            if row.oiorderid and row.menucompid:
                # found avoid component clash
                # should be a set
                kitchen_list[row.cid].incompatible_components.append(
                    row.component)
            # we Know that it is not incommpatible
            elif (row.component not in
                  kitchen_list[row.cid].incompatible_components):
                # found new other avoid component that does not clash today
                # should be a set
                kitchen_list[row.cid].other_components.append(
                    row.component)
        # END FOR

        rows = db_sa_session.execute(q_day_res)
        for row in rows:
            check_for_new_client(kitchen_list, row)
            if row.oiorderid and row.menucompid:
                # found restriction clash
                # should be a sorted set
                kitchen_list[row.cid].incompatible_ingredients.append(
                    row.ingredient)
            elif (row.ingredient and row.ingredient not in
                  kitchen_list[row.cid].incompatible_ingredients):
                # found new other restriction that does not clash today
                # should be a set
                kitchen_list[row.cid].other_ingredients.append(
                    row.ingredient)
            kitchen_list[row.cid].restricted_items.append(
                row.restricted_item)
        # END FOR

        rows = db_sa_session.execute(q_day_pre)
        for row in rows:
            check_for_new_client(kitchen_list, row)
            # should be a sorted set
            # found client with food preparation
            kitchen_list[row.cid].preparation.append(row.food_prep)
        # END FOR

        # Components summary for the day
        rows = db_sa_session.execute(q_day_del_lis)
        for row in rows:
            check_for_new_client(kitchen_list, row)
            if row.component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH:
                kitchen_list[row.cid].meal_qty = \
                    kitchen_list[row.cid].meal_qty + row.total_quantity
                kitchen_list[row.cid].meal_size = row.size
            kitchen_list[row.cid].meal_components[row.component_group] = \
                MealComponent(id=row.component_id,
                              name=row.component_name,
                              qty=row.total_quantity)
        # END FOR

        # sort requirements list in each value
        for value in kitchen_list.values():
            value.incompatible_ingredients.sort()
            value.incompatible_components.sort()
            value.other_ingredients.sort()
            value.other_components.sort()
            value.restricted_items.sort()
            value.preparation.sort()

        return kitchen_list

# get_kitchen_items helper classes and functions

MealComponent = \
    collections.namedtuple('MealComponent', ['id', 'name', 'qty'])


class KitchenItem(object):
    # meal specifics for an order

    def __init__(self):

        self.lastname = None
        self.firstname = None
        self.meal_qty = 0
        self.meal_size = ''
        self.incompatible_ingredients = []
        self.incompatible_components = []
        self.other_ingredients = []
        self.other_components = []
        self.restricted_items = []
        self.preparation = []
        self.meal_components = {}
        #  key is a component_group,
        #  value is a MealComponent named tuple

    def __str__(self):
        return("[" +
               'lastname=' + self.lastname + ', ' +
               'firstname=' + self.firstname + ', ' +
               'meal_qty=' + str(self.meal_qty) + ', ' +
               'meal_size=' + str(self.meal_size) + ', ' +
               'clash_ingre=' +
               repr(self.incompatible_ingredients) + ', ' +
               'clash_compo=' +
               repr(self.incompatible_components) + ', ' +
               'avoid_ingre=' + repr(self.other_ingredients) + ', ' +
               'avoid_compo=' + repr(self.other_components) + ', ' +
               'restr_items=' + repr(self.restricted_items) + ', ' +
               'meal_components=' + repr(
                   sorted(self.meal_components.items())) + ', ' +
               'preparation=' + repr(self.preparation) + ']')


def print_rows(q, heading=""):  # DEBUG
    # print("\n-----------------------------------------------------\n",
    #       # q, "\n",
    #       heading)
    # rows = db_sa_session.execute(q)
    # for row in rows:
    #     print(row)
    pass


def check_for_new_client(kitchen_list, row):
    # add client in list when first found
    if not kitchen_list.get(row.cid):
        # found new client
        kitchen_list[row.cid] = KitchenItem()
        kitchen_list[row.cid].lastname = row.lastname
        kitchen_list[row.cid].firstname = row.firstname

# End kitchen items helpers


class OrderFilter(FilterSet):

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    status = ChoiceFilter(
        choices=(('', ''),) + ORDER_STATUS
    )

    class Meta:
        model = Order
        fields = ['status', 'delivery_date']

    @staticmethod
    def filter_search(queryset, value):
        if not value:
            return queryset

        names = value.split(' ')

        name_contains = Q()

        for name in names:
            firstname_contains = Q(
                client__member__firstname__icontains=name
            )

            name_contains |= firstname_contains

            lastname_contains = Q(
                client__member__lastname__icontains=name
            )
            name_contains |= lastname_contains

        return queryset.filter(
            name_contains
        )


class Order_item(models.Model):

    class Meta:
        verbose_name_plural = _('order items')

    order = models.ForeignKey(
        'order.Order',
        verbose_name=_('order'),
        related_name='orders',
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_('price')
    )

    billable_flag = models.BooleanField(
        verbose_name=_('billable flag'),
    )

    size = models.CharField(
        verbose_name=_('size'),
        max_length=1,
        null=True,
        choices=SIZE_CHOICES,
    )

    order_item_type = models.CharField(
        verbose_name=_('order item type'),
        max_length=20,
        choices=ORDER_ITEM_TYPE_CHOICES,
    )

    remark = models.CharField(
        max_length=256,
        verbose_name=_('remark')
    )

    total_quantity = models.IntegerField(
        verbose_name=_('total quantity'),
        null=True,
    )

    free_quantity = models.IntegerField(
        verbose_name=_('free quantity'),
        null=True,
    )

    component_group = models.CharField(
        max_length=100,
        choices=COMPONENT_GROUP_CHOICES,
        verbose_name=_('component group'),
        null=True,
    )

    def __str__(self):
        return "<For delivery on:> {} <order_item_type:>" \
            " {} <component_group:> {}".\
            format(str(self.order.delivery_date),
                   self.order_item_type,
                   self.component_group)
