import collections
from datetime import date, datetime
import re

from django.db import models, connection
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django_filters import FilterSet, MethodFilter, ChoiceFilter
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from member.models import (Client, Member, Route,
                           RATE_TYPE_LOW_INCOME, RATE_TYPE_SOLIDARY,
                           Address, Option, Client_option, Restriction,
                           Client_avoid_ingredient, Client_avoid_component,
                           OPTION_GROUP_CHOICES_PREPARATION)
from meal.models import (Menu, Menu_component, Component,
                         Restricted_item, Ingredient,
                         Component_ingredient, Incompatibility,
                         COMPONENT_GROUP_CHOICES,
                         COMPONENT_GROUP_CHOICES_MAIN_DISH,
                         COMPONENT_GROUP_CHOICES_SIDES)


ORDER_STATUS = (
    ('O', _('Ordered')),
    ('D', _('Delivered')),
    ('N', _('No Charge')),
    ('C', _('Cancelled')),
    ('B', _('Billed')),
    ('P', _('Paid')),
)

ORDER_STATUS_ORDERED = ORDER_STATUS[0][0]

SIZE_CHOICES = (
    ('', _('Serving size')),
    ('R', _('Regular')),
    ('L', _('Large')),
)

SIZE_CHOICES_REGULAR = SIZE_CHOICES[1][0]
SIZE_CHOICES_LARGE = SIZE_CHOICES[2][0]

ORDER_ITEM_TYPE_CHOICES = (
    ('meal_component',
        _('Meal component (main dish, vegetable, side dish, seasonal)')),
    ('delivery', _('Delivery (general store item, invitation, ...)')),
    ('pickup', _('Pickup (payment)')),
    ('visit', _('Visit')),
)

ORDER_ITEM_TYPE_CHOICES_COMPONENT = ORDER_ITEM_TYPE_CHOICES[1][0]

MAIN_PRICE_DEFAULT = 8.00  # TODO use decimal ?
SIDE_PRICE_DEFAULT = 1.00
MAIN_PRICE_LOW_INCOME = 7.00
SIDE_PRICE_LOW_INCOME = 0.75
MAIN_PRICE_SOLIDARY = 6.00
SIDE_PRICE_SOLIDARY = 0.50


class OrderManager(models.Manager):

    def get_shippable_orders(self, delivery_date=None):
        """
        Return the orders ready to be delivered for a given date.
        A shippable order must be created in the database, and its ORDER_STATUS
        must be 'O' (Ordered).
        """
        # If no date is passed, use the current day
        if delivery_date is None:
            delivery_date = date.today()
        return self.get_queryset().filter(
            delivery_date=delivery_date,
            status=ORDER_STATUS_ORDERED,
            client__status=Client.ACTIVE).order_by(
                'client__route__pk', 'pk'
            )

    def get_shippable_orders_by_route(self, route_id):
        """
        Return the orders ready to be delivered for a given route.
        It is assumed here that the delivery date is today.
        A shippable order must be created in the database, and its ORDER_STATUS
        must be 'O' (Ordered).
        """
        delivery_date = date.today()
        return self.get_queryset().filter(
            delivery_date=delivery_date,
            status=ORDER_STATUS_ORDERED,
            client__route=route_id,
            client__status=Client.ACTIVE)

    def get_billable_orders(self, year, month):
        """
        Return the orders that have successfully delivered during
        the given period.
        A period is represented by a year and a month.
        """
        return self.get_queryset().filter(
            delivery_date__year=year,
            delivery_date__month=month,
            status='D',
        )

    def get_billable_orders_client(self, month, year, client):
        """
        Return the orders that have successfully delivered during
        the given period to a given client.
        A period is represented by a year and a month.
        """
        return self.get_queryset().filter(
            delivery_date__year=year,
            delivery_date__month=month,
            client=client,
            status="D",
        )

    def get_client_prices(self, client):
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

        return {'main': main_price, 'side': side_price}

    def auto_create_orders(self, delivery_date, clients):
        """
        Automatically creates orders and order items for the given delivery
        date and given client list.
        Order items will be created based on client's meals default.

        Parameters:
          delivery_date : date on which orders are to be delivered
          clients : a list of one or many client objects

        Returns:
          Number of orders created.
        """
        created = 0
        orders = []
        day = delivery_date.weekday()  # Monday is 0, Sunday is 6
        for client in clients:
            # No main_dish means no delivery this day
            main_dish_quantity, main_dish_size = Client.get_meal_defaults(
                client,
                COMPONENT_GROUP_CHOICES_MAIN_DISH, day)
            if main_dish_quantity == 0:
                continue
            try:
                # If an order is already created, skip order items creation
                # (if want to replace, must be deleted first)
                order = Order.objects.get(client=client,
                                          delivery_date=delivery_date)
                orders.append(order)
                continue
            except Order.DoesNotExist:
                order = Order.objects.create(client=client,
                                             creation_date=datetime.today(),
                                             delivery_date=delivery_date,
                                             status=ORDER_STATUS_ORDERED)
                created += 1
                orders.append(order)

            # TODO Use Parameters Model in member to store unit prices
            prices = self.get_client_prices(client)
            main_price = prices['main']
            side_price = prices['side']

            for component_group, trans in COMPONENT_GROUP_CHOICES:
                item_quantity, item_size = Client.get_meal_defaults(
                    client, component_group, day)
                if item_quantity > 0:
                    # Set the quantity of the current item
                    total_quantity = item_quantity
                    # Set the unit price of the current item
                    if (component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH):
                        unit_price = main_price
                    else:
                        unit_price = side_price
                        while main_dish_quantity > 0 and item_quantity > 0:
                            main_dish_quantity -= 1
                            item_quantity -= 1
                    Order_item.objects.create(
                        order=order,
                        component_group=component_group,
                        price=total_quantity * unit_price,
                        billable_flag=True,
                        size=item_size,
                        order_item_type=ORDER_ITEM_TYPE_CHOICES_COMPONENT,
                        total_quantity=total_quantity)
        return orders

    def create_batch_orders(self, delivery_dates, client, items,
                            return_created_orders=False):
        created_orders = []
        messages = []

        # Calculate client prices (main and side)
        prices = self.get_client_prices(client)

        for delivery_date_str in delivery_dates:
            delivery_date = datetime.strptime(
                delivery_date_str, "%Y-%m-%d"
            ).date()
            try:
                Order.objects.get(client=client, delivery_date=delivery_date)
                # If an order is already created, skip order items creation
                # (if want to replace, must be deleted first)
            except Order.DoesNotExist:
                # If no order for this client/date, create it and attach items
                individual_items = {}
                for key, value in items.items():
                    if delivery_date_str in key:
                        replaced_key = key.replace(
                            delivery_date_str,
                            'default'
                        )
                        individual_items[replaced_key] = value
                order = self.create_order(
                    delivery_date, client, individual_items, prices
                )
                created_orders.append(order)

        if not return_created_orders:
            return len(created_orders)   # LXYANG: TO BE DEPRECATED
        else:
            return created_orders

    def create_order(self, delivery_date, client, items, prices):
        order = Order.objects.create(client=client,
                                     delivery_date=delivery_date)

        for component_group, trans in COMPONENT_GROUP_CHOICES:
            if component_group != COMPONENT_GROUP_CHOICES_SIDES:
                item_qty = items[component_group + '_default_quantity']
                item_pri = prices['side']
                item_siz = None
                if (item_qty):
                    if (component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH):
                        item_pri = prices['main']
                        item_siz = items['size_default']

                    Order_item.objects.create(
                        order=order,
                        component_group=component_group,
                        price=item_qty * item_pri,
                        billable_flag=True,
                        size=item_siz,
                        order_item_type=ORDER_ITEM_TYPE_CHOICES_COMPONENT,
                        total_quantity=item_qty)

        return order


class Order(models.Model):

    class Meta:
        verbose_name_plural = _('orders')
        ordering = ['-delivery_date']

    # Order information
    creation_date = models.DateField(
        verbose_name=_('creation date'),
        auto_now_add=True
    )

    delivery_date = models.DateField(
        verbose_name=_('delivery date')
    )

    status = models.CharField(
        max_length=1,
        choices=ORDER_STATUS,
        verbose_name=_('order status'),
        default=ORDER_STATUS_ORDERED
    )

    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='client_order',
        blank=False,
        default=""
    )

    objects = OrderManager()

    def get_absolute_url(self):
        return reverse('order:view', kwargs={'pk': self.pk})

    @property
    def price(self):
        """
        Sum the items prices for the given order.
        """
        total = 0
        for item in self.orders.all():
            if item.billable_flag is True:
                total = total + item.price
        return total

    def add_item(self, type, **kwargs):
        """
        Add a new item to the given order.
        """
        quantity = kwargs.get('total_quantity', 1)
        billable = kwargs.get('billable', True)
        Order_item.objects.create(
            order=self,
            component_group=kwargs.get('component_group', ''),
            price=quantity * MAIN_PRICE_DEFAULT if billable else 0,
            billable_flag=billable,
            size=kwargs.get('size', 'R'),
            order_item_type=type,
            total_quantity=quantity)

    def remove_item(self, order_item_id):
        """
        Remove an existing item from the order.
        """
        self.orders.remove(order_item_id)

    def cancel(self):
        """
        Cancel the given order.
        """
        # 'C' = Cancelled
        self.status = 'C'
        self.save()

    def __str__(self):
        return "client={}, delivery_date={}".format(
            self.client,
            self.delivery_date
        )

    @staticmethod
    def get_kitchen_items(delivery_date):
        """Get all client meal order specifics for delivery date.

        For each client that has ordered a meal for 'delivery_date',
        find all the information needed for the Kitchen Count Report
        and the Meal Labels. This information is stored in KitchenItem
        objects. (See KitchenItem for description of each attribute).

        Args:
            delivery_date: A datetime.date object, the date on which
                the meals will be delivered to the clients.

        Returns:
            A dictionary where the key is an Integer 'client id' and
            the value is a KitchenItem named tuple.
        """
        kitchen_list = {}

        # Day's avoid ingredients clashes.
        for row in day_avoid_ingredient(delivery_date):
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
            if (row.ingredient not in
                    kitchen_list[row.cid].avoid_ingredients):
                # remember ingredient to avoid
                kitchen_list[row.cid].avoid_ingredients.append(
                    row.ingredient)

        # Day's restrictions.
        for row in day_restrictions(delivery_date):
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
            if (row.restricted_item not in
                    kitchen_list[row.cid].restricted_items):
                # remember restricted_item
                kitchen_list[row.cid].restricted_items.append(
                    row.restricted_item)

        # Day's preparations.
        for row in day_preparations(delivery_date):
            check_for_new_client(kitchen_list, row)
            # should be a sorted set
            # found client with food preparation
            kitchen_list[row.cid].preparation.append(row.food_prep)

        # Day's Delivery Items, Components summary and Data for all labels.
        for row in day_delivery_items(delivery_date):
            check_for_new_client(kitchen_list, row)
            if row.component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH:
                kitchen_list[row.cid] = kitchen_list[row.cid]._replace(
                    meal_qty=(kitchen_list[row.cid].meal_qty +
                              row.total_quantity),
                    meal_size=row.size)
            kitchen_list[row.cid].meal_components[row.component_group] = \
                MealComponent(id=row.component_id,
                              name=row.component_name,
                              qty=row.total_quantity)
            kitchen_list[row.cid] = kitchen_list[row.cid]._replace(
                routename=row.routename)

        # Sort requirements list in each value.
        for value in kitchen_list.values():
            value.incompatible_ingredients.sort()
            value.other_ingredients.sort()
            value.restricted_items.sort()
            value.preparation.sort()

        return kitchen_list

    @staticmethod
    def get_delivery_list(delivery_date, route_id):
        """Get all delivery order specifics for delivery date and route.

        For each client that has ordered a meal for 'delivery_date'
        and that belongs to the route specified, find all the
        information needed to generate the Route Sheet. This
        information is stored in DeliveryClient objects. (See
        DeliveryClient for the attributes).

        Args:
            delivery_date: A datetime.date object, the date on which
                the meals will be delivered to the clients.
            route_id: An integer, the is of the route for which the
                delivery list must be produced.

        Returns:
            A dictionary where the key is an Integer 'client id' and
            the value is a DeliveryClient object.
        """
        orditms = Order_item.objects.\
            select_related('order__client__member__address').\
            filter(
                order__delivery_date=delivery_date,
                order__client__route__id=route_id).\
            order_by('order__client_id')

        route_list = {}
        for oi in orditms:
            if not route_list.get(oi.order.client.id):
                # found new client
                route_list[oi.order.client.id] = DeliveryClient(
                    oi.order.client.member.firstname,
                    oi.order.client.member.lastname,
                    oi.order.client.member.address.number,
                    oi.order.client.member.address.street,
                    oi.order.client.member.address.apartment,
                    # TODO idea : get list of member ids, later select
                    #   contacts and loop to add phone number
                    (oi.order.client.member.home_phone or
                     oi.order.client.member.cell_phone),
                    oi.order.client.delivery_note,
                    delivery_items=[])
            # found new delivery item for client
            route_list[oi.order.client.id].delivery_items.append(
                DeliveryItem(
                    oi.component_group,
                    oi.total_quantity,
                    oi.order_item_type,
                    oi.remark,
                    size=(
                        oi.size if
                        oi.component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH
                        else '')))

        # Sort delivery items for each client
        for client in route_list.values():
            client.delivery_items.sort(key=component_group_sorting)

        return route_list

# Order.get_kitchen_items helper functions.


def named_tuple_fetchall(cursor):
    """Fetch all rows from a database 'cursor', returning namedtuples.

    Args:
        cursor: A database cursor object on which a query was executed.

    Returns:
        A list of named tuples, each one being a row fetched from the cursor.
        Each column of the cursor becomes an attribute of the named tuple.
    """
    desc = cursor.description
    nt_row = collections.namedtuple('Row', [col[0] for col in desc])
    return [nt_row(*row) for row in cursor.fetchall()]


def sql_prep(query, valuesdict):
    """Prepare SQL 'query' by matching its parameters with given 'values'.

    Find parameters %(name)s in 'query' and replace them with a %s placeholder
    then build an ordered list of corresponding values.

    Args:
        query: A string, the SQL query containing parameters like %(name)s.
        valuesdict: A dictionary of parameter values : {'name': value, ...}.

    Returns:
        A tuple of two values, (the modified query string, a list of values to
        pass to the query). For example :

        >>> sql_prep('this is %(one)s a trial of %(two)s changes %(one)s end',
                     {'one': 10, 'two': 'twenty'})
        ('this is %s a trial of %s changes %s end', [10, 'twenty', 10])

    Raises:
        Exception: A parameter in the query does not have a matching value.
    """
    # Get all the substrings that match the regex
    subs = [(m.start(), m.end(), m.group(0))
            for m in re.finditer(r"%\(\w+\)s", query)]
    # print("subs", subs)  # DEBUG
    mod = []    # list of segments of new query
    pos = 0     # start of non-matching text in old query
    names = []  # parameter names found in old query
    for sta, end, grp in subs:
        mod.append(query[pos:sta])  # add text before match
        mod.append("%s")            # new placeholder
        pos = end                   # next non-matching text
        names.append(grp[2:-2])     # extract name in %(name)s
    mod.append(query[pos:])  # add tail of old query
    values = []
    for n in names:
        val = valuesdict.get(n)
        if val:
            values.append(val)
        else:
            raise Exception(
                "Query parameter '{}' not found in values".format(n))
    return ''.join(mod), values


def sql_exec(query, values, heading=''):
    """Execute SQL 'query' passing to it the given 'values'.

    Args:
        query: A string, the SQL query containing parameters like %(name)s.
        values: A dictionary of parameter values : {'name': value, ...}.
        heading: A string that if we debug, will be printed once before
            all the result rows.

    Returns:
        A list of named tuples, each one is a row returned by the database
        as the result of the SQL query.
    """
    with connection.cursor() as cursor:
        cursor.execute(*sql_prep(query, values))
        rows = named_tuple_fetchall(cursor)
    # UNCOMMENT THESE LINES FOR DEBUGGING; DO NOT REMOVE
    # print("\n-----------------------------------------------------\n",
    #       heading, "\n")
    # for row in rows:
    #     print(row)
    #
    return rows


def day_avoid_ingredient(delivery_date):
    """ Get day's avoid ingredients clashes.

    For each client that has ordered a meal for 'delivery_date', find all
    the ingredients that he avoids and identify which of those
    ingredients are included in the main dish for 'delivery_date'.
    Note that the 'avoid ingredients' are the ones that the client specified
    explicitly.

    Args:
        delivery_date: A datetime.date object, the date on which the meals will
            be delivered to the clients.

    Returns:
        A list of named tuples, each one containing the columns specified
        in the SELECT clause.
    """
    query = """
    SELECT member_client.id AS cid,
      member_member.firstname, member_member.lastname,
      order_order.id AS oid,
      order_order.delivery_date,
      meal_menu.id AS menuid,
      meal_menu_component.id AS menucompid,
      meal_ingredient.name AS ingredient,
      meal_component.name,
      order_order_item.id AS oiid,
      order_order_item.order_id AS oiorderid
    FROM member_member
      JOIN member_client ON member_client.member_id = member_member.id
      JOIN order_order ON order_order.client_id = member_client.id
      JOIN meal_menu ON meal_menu.date =                      %(delivery_date)s
      JOIN member_client_avoid_ingredient ON
        member_client_avoid_ingredient.client_id = member_client.id
      JOIN meal_ingredient ON
        meal_ingredient.id = member_client_avoid_ingredient.ingredient_id
      LEFT OUTER JOIN meal_component_ingredient ON
        meal_component_ingredient.ingredient_id = meal_ingredient.id AND
          meal_component_ingredient.date =                    %(delivery_date)s
      LEFT OUTER JOIN meal_component ON
        meal_component.id = meal_component_ingredient.component_id
      LEFT OUTER JOIN order_order_item ON
        order_order_item.component_group = meal_component.component_group AND
          order_order_item.order_id = order_order.id
      LEFT OUTER JOIN meal_menu_component ON
        meal_menu_component.component_id = meal_component.id AND
          meal_menu_component.menu_id = meal_menu.id
    WHERE order_order.delivery_date =                         %(delivery_date)s
    ORDER BY member_client.id
    """
    values = {'delivery_date': delivery_date}
    return sql_exec(query, values, "****** Avoid ingredients ******")


def day_restrictions(delivery_date):
    """ Get day's restrictions.

    For each client that has ordered a meal for 'delivery_date', find all
    the ingredients that correspond to the restricted items that he specified
    and identify which of those ingredients are included in the main dish
    for 'delivery_date'.

    Args:
        delivery_date: A datetime.date object, the date on which the meals will
            be delivered to the clients.

    Returns:
        A list of named tuples, each one containing the columns specified
        in the SELECT clause.
    """
    query = """
    SELECT member_client.id AS cid,
      member_member.firstname, member_member.lastname,
      order_order.id AS oid,
      order_order.delivery_date,
      meal_menu.id AS menuid,
      meal_menu_component.id AS menucompid,
      meal_restricted_item.name AS restricted_item,
      meal_ingredient.name AS ingredient,
      meal_component.name,
      order_order_item.id AS oiid,
      order_order_item.order_id AS oiorderid
    FROM member_member
      JOIN member_client ON member_client.member_id = member_member.id
      JOIN order_order ON order_order.client_id = member_client.id
      JOIN meal_menu ON meal_menu.date =                      %(delivery_date)s
      JOIN member_restriction ON
        member_restriction.client_id = member_client.id
      JOIN meal_restricted_item ON
        meal_restricted_item.id = member_restriction.restricted_item_id
      LEFT OUTER JOIN meal_incompatibility ON
        meal_incompatibility.restricted_item_id =
          member_restriction.restricted_item_id
      LEFT OUTER JOIN meal_ingredient ON
        meal_incompatibility.ingredient_id = meal_ingredient.id
      LEFT OUTER JOIN meal_component_ingredient ON
        meal_component_ingredient.ingredient_id = meal_ingredient.id AND
          meal_component_ingredient.date =                    %(delivery_date)s
      LEFT OUTER JOIN meal_component ON
        meal_component_ingredient.component_id = meal_component.id
      LEFT OUTER JOIN order_order_item ON
       order_order_item.component_group = meal_component.component_group AND
         order_order_item.order_id = order_order.id
      LEFT OUTER JOIN meal_menu_component ON
        meal_menu_component.component_id = meal_component.id AND
          meal_menu_component.menu_id = meal_menu.id
    WHERE order_order.delivery_date =                         %(delivery_date)s
    ORDER BY member_client.id
    """
    values = {'delivery_date': delivery_date}
    return sql_exec(query, values, "****** Restrictions ******")


def day_preparations(delivery_date):
    """ Get day's preparations.

    For each client that has ordered a meal for 'delivery_date', find all
    the food preparations that he specified.

    Args:
        delivery_date: A datetime.date object, the date on which the meals will
            be delivered to the clients.

    Returns:
        A list of named tuples, each one containing the columns specified
        in the SELECT clause.
    """
    query = """
    SELECT member_client.id AS cid,
      member_member.firstname, member_member.lastname,
      member_option.name AS food_prep,
      order_order.id AS oid,
      order_order.delivery_date
    FROM member_member
      JOIN member_client ON member_client.member_id = member_member.id
      JOIN member_client_option ON
        member_client_option.client_id = member_client.id
      JOIN member_option ON member_option.id = member_client_option.option_id
      JOIN order_order ON order_order.client_id = member_client.id
    WHERE order_order.delivery_date =                     %(delivery_date)s AND
      member_option.option_group =                             %(option_group)s
    ORDER BY member_member.lastname, member_member.firstname
    """
    values = {'delivery_date': delivery_date,
              'option_group': OPTION_GROUP_CHOICES_PREPARATION}
    return sql_exec(query, values, "****** Preparations ******")


def day_delivery_items(delivery_date):
    """ Get day's Delivery Items.

    For each client that has ordered a meal for 'delivery_date', find his route
    and all the details and quantities for the items that have to delivered.

    Args:
        delivery_date: A datetime.date object, the date on which the meals will
            be delivered to the clients.

    Returns:
        A list of named tuples, each one containing the columns specified
        in the SELECT clause.
    """
    query = """
    SELECT member_client.id AS cid,
      member_member.firstname, member_member.lastname,
      member_route.name AS routename,
      order_order_item.total_quantity, order_order_item.size,
      meal_menu.id AS menuid,
      meal_menu_component.id AS mencomid,
      meal_component.id AS component_id, meal_component.component_group,
      meal_component.name AS component_name
    FROM member_member
      JOIN member_client ON member_client.member_id = member_member.id
      JOIN member_route ON member_route.id = member_client.route_id
      JOIN meal_menu ON meal_menu.date =                      %(delivery_date)s
      JOIN order_order ON order_order.client_id = member_client.id
      JOIN order_order_item ON order_order_item.order_id = order_order.id
      JOIN meal_menu_component ON meal_menu_component.menu_id = meal_menu.id
      JOIN meal_component ON
        meal_component.id = meal_menu_component.component_id AND
          meal_component.component_group = order_order_item.component_group
    WHERE order_order.delivery_date =                         %(delivery_date)s
    ORDER BY member_member.lastname, member_member.firstname
    """
    values = {'delivery_date': delivery_date}
    return sql_exec(query, values, "****** Delivery List ******")


KitchenItem = collections.namedtuple(         # Meal specifics for an order.
    'KitchenItem',
    ['lastname',                     # Client's lastname
     'firstname',                    # Client's firstname
     'routename',                    # Name of Client's route (ex. 'Mile-end')
     'meal_qty',                     # Quantity of main dish servings
     'meal_size',                    # Size of main dish
     'incompatible_ingredients',     # Ingredients in main dish that clash
     'other_ingredients',            # Other ingredients that client refuses
     'avoid_ingredients',            # All ingredients to avoid for the client
     'restricted_items',             # All restricted items for the client
     'preparation',                  # All food preparations for the client
     'meal_components'])             # List of MealComponents objects


MealComponent = collections.namedtuple(       # Component specifics for a meal.
    'MealComponent',
    ['id',                           # Component id
     'name',                         # Component name (ex. 'Rice pudding')
     'qty'])                         # Quantity of this component in the order


def check_for_new_client(kitchen_list, row):
    """ Add KitchenItem entry when client is found the first time.

    Modifies kitchen_list by adding an entry.

    Args:
        kitchen_list: A dictionary where the key is an Integer 'client id'
            and the value is a KitchenItem named tuple.
        row: An object having an attribute 'cid' that represents
            an Integer 'client id'.
    """
    if not kitchen_list.get(row.cid):
        # found new client
        kitchen_list[row.cid] = KitchenItem(
            lastname=row.lastname,
            firstname=row.firstname,
            routename=None,
            meal_qty=0,
            meal_size='',
            incompatible_ingredients=[],
            other_ingredients=[],
            avoid_ingredients=[],
            restricted_items=[],
            preparation=[],
            meal_components={})

# End Order.kitchen items helpers


# Order.get_delivery_list helper functions.


DeliveryClient = collections.namedtuple(  # Delivery details for client order.
    'DeliveryClient',
    ['firstname',
     'lastname',
     'number',
     'street',
     'apartment',
     'phone',
     'delivery_note',
     'delivery_items'])  # list of DeliveryItem objects


DeliveryItem = collections.namedtuple(    # Item contained in a delivery.
    'DeliveryItem',
    ['component_group',    # String if item is a meal component, else None
     'total_quantity',     # Quantity of item to deliver
     'order_item_type',    # Type of item to deliver (ex. dish, bill, grocery)
     'remark',
     'size'])              # Size of item if applicable


def component_group_sorting(component):
    """Sorting sequence for object according to their component_group.

    The sequence is ordered such that the 'main dish' object is first,
    then all the objects having a component_group such as 'dessert',
    'green salad' etc. in alphabetical order, and finally objects
    having an empty component_group.

    Args:
        component: A object having a 'component_group' attribute.

    Returns:
        A string, that can be used as a key to a sort function.
    """
    if component.component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH:
        return '1'
    elif component.component_group != '':
        return '2' + component.component_group
    else:
        return '3'

# End Order.get_delivery_list helpers


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


class DeliveredOrdersByMonth(FilterSet):

    delivery_date = MethodFilter(
        action='filter_period'
    )

    class Meta:
        model = Order

    @staticmethod
    def filter_period(queryset, value):
        if not value:
            return None

        year, month = value.split('-')
        return queryset.filter(
            status="D",
            delivery_date__year=year,
            delivery_date__month=month,
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
        verbose_name=_('remark'),
        null=True,
        blank=True,
    )

    total_quantity = models.IntegerField(
        verbose_name=_('total quantity'),
        null=True,
        blank=True,
    )

    free_quantity = models.IntegerField(
        verbose_name=_('free quantity'),
        null=True,
        blank=True,
    )

    component_group = models.CharField(
        max_length=100,
        choices=COMPONENT_GROUP_CHOICES,
        verbose_name=_('component group'),
        null=True,
        blank=True,
    )

    def __str__(self):
        return "<For delivery on:> {} <order_item_type:>" \
            " {} <component_group:> {}".\
            format(str(self.order.delivery_date),
                   self.order_item_type,
                   self.component_group)


class OrderStatusChange(models.Model):

    class Meta:
        ordering = ['change_time']

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_changes"
    )

    status_from = models.CharField(
        max_length=1,
        choices=ORDER_STATUS
    )

    status_to = models.CharField(
        max_length=1,
        choices=ORDER_STATUS
    )

    reason = models.CharField(
        max_length=200,
        blank=True,
        default=''
    )

    change_time = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return "Order #{} status update: from {} to {}, on {}".format(
            self.order.pk,
            self.get_status_from_display(),
            self.get_status_to_display(),
            self.change_time
        )

    def clean(self):
        """
        Make sure this is valid in regards to Order.
        """
        if self.order.status != self.status_from:
            raise ValidationError(
                _("Invalid order status update."),
                code='status_from_incorrect'
            )

    def save(self, *a, **k):
        """ Process a scheduled change when saving."""
        self.full_clean()  # we defined clean method so we need to override
        super(OrderStatusChange, self).save(*a, **k)
        self.order.status = self.status_to
        self.order.save()
