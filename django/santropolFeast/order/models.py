from django.db import models
from django.db.models import Q
from member.models import Client, Member
from member.models import RATE_TYPE_LOW_INCOME, RATE_TYPE_SOLIDARY
from meal.models import Menu, Menu_component, Component
from meal.models import COMPONENT_GROUP_CHOICES_MAIN_DISH
from django.utils.translation import ugettext_lazy as _
from django_filters import FilterSet, MethodFilter, ChoiceFilter
from member.apps import MemberConfig

ORDER_STATUS_CHOICES = (
    ('O', _('Ordered')),
    ('D', _('Delivered')),
    ('B', _('Billed')),
    ('P', _('Paid')),
)

ORDER_STATUS_CHOICES_ORDERED = ORDER_STATUS_CHOICES[0][0]

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

        return self.get_queryset().filter(
            delivery_date=delivery_date
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
        choices=ORDER_STATUS_CHOICES,
        verbose_name=_('order status')
    )

    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('client'),
        related_name='client_order',
    )

    objects = OrderManager()

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

        Static method called only on class object.

        Parameters:
          creation_date : date on which orders are created
          delivery_date : date on which orders are to be delivered
          clients : a list of one or many client objects

        Returns:
          Number of orders created.

        Raises :
          Exception if no menu yet for delivery date.
        """

        # session for SQLAlchemy
        session = MemberConfig.Session()
        num_orders_created = 0
        qcomp = session.query(Component.sa.id.label('compid')).\
            select_from(Menu.sa).\
            join(Menu_component.sa,
                 Menu_component.sa.menu_id == Menu.sa.id).\
            join(Component.sa,
                 Component.sa.id == Menu_component.sa.component_id).\
            filter(Menu.sa.date == delivery_date)
        # print ("count=", qcomp.count())  # DEBUG
        if not qcomp.count():
            raise Exception(
                "No menu for delivery date= " + str(delivery_date))
        components = \
            [Component.objects.get(pk=row.compid) for row in qcomp.all()]
        # print("Menu on ", date, " : ", (components))  #DEBUG
        day = delivery_date.weekday()  # Monday is 0, Sunday is 6
        for client in clients:
            # find quantity of free side dishes based on number of main dishes
            free_side_dish_qty = Client.get_meal_defaults(
                client,
                COMPONENT_GROUP_CHOICES_MAIN_DISH, day)[0]
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
                              status=ORDER_STATUS_CHOICES_ORDERED)
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
            for component in components:
                default_qty, default_size = \
                    Client.get_meal_defaults(
                        client, component.component_group, day)
                if default_qty > 0:
                    total_quantity = default_qty
                    free_quantity = 0
                    if (component.component_group ==
                            COMPONENT_GROUP_CHOICES_MAIN_DISH):
                        unit_price = main_price
                    else:
                        unit_price = side_price
                        while free_side_dish_qty > 0 and default_qty > 0:
                            free_side_dish_qty -= 1
                            default_qty -= 1
                            free_quantity += 1
                    oi = Order_item(
                        order=order,
                        component=component,
                        price=(total_quantity - free_quantity) * unit_price,
                        billable_flag=True,
                        size=default_size,
                        order_item_type=ORDER_ITEM_TYPE_CHOICES_COMPONENT,
                        total_quantity=total_quantity,
                        free_quantity=free_quantity)
                    oi.save()
        # print("Number of orders created = ", num_orders_created) #DEBUG
        return num_orders_created


class OrderFilter(FilterSet):

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    status = ChoiceFilter(
        choices=(('', ''),) + ORDER_STATUS_CHOICES
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

        return queryset.filter(name_contains)


class Order_item(models.Model):

    class Meta:
        verbose_name_plural = _('order items')

    order = models.ForeignKey(
        'order.Order',
        verbose_name=_('order'),
        related_name='orders',
    )

    component = models.ForeignKey(
        'meal.Component',
        verbose_name=_('component'),
        null=True,
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
