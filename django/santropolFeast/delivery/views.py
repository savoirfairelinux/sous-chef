from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from delivery.models import Delivery

from .apps import DeliveryConfig

from sqlalchemy import func, or_, and_

import datetime

from meal.models import Component, Restricted_item, Ingredient
from meal.models import Component_ingredient, Incompatibility
from meal.models import Menu, Menu_component
from member.models import Member, Client, Contact, Address, Note, Referencing
from member.models import Route, Note, Option, Client_option, Restriction
from member.models import Client_avoid_ingredient, Client_avoid_component
from notification.models import Notification
from order.models import Order, Order_item


class Orderlist(generic.ListView):
    # Display all the order on a given day
    model = Delivery
    template_name = 'order.html'


class MealInformation(generic.ListView):
    # Display all the meal and alert for a given day
    model = Delivery
    template_name = 'information.html'


class RoutesInformation(generic.ListView):
    # Display all the route information for a given day
    model = Delivery
    template_name = "routes.html"


class Kitchen_item(object):
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

    def __str__(self):
        return("[" +
               'lastname=' + self.lastname + ', ' +
               'firstname=' + self.firstname + ', ' +
               'meal_qty=' + str(self.meal_qty) + ', ' +
               'meal_size=' + str(self.meal_size) + ', ' +
               'clash_ingre=' + repr(self.incompatible_ingredients) + ', ' +
               'clash_compo=' + repr(self.incompatible_components) + ', ' +
               'avoid_ingre=' + repr(self.other_ingredients) + ', ' +
               'avoid_compo=' + repr(self.other_components) + ', ' +
               'restr_items=' + repr(self.restricted_items) + ', ' +
               'preparation=' + repr(self.preparation) + ']')


class Line(object):
    def __init__(self,
                 client='', qty='', size='', incom='', restr='', prep=''):
        self.client = client
        self.qty = qty
        self.size = size
        self.incom = incom
        self.restr = restr
        self.prep = prep


def print_rows(q, heading=""):
    pass
    # print("\n-----------------------------------------------------\n",
    #       # q, "\n",
    #       heading)
    # for row in q.all():
    #     print(row)


def kcr_view(request):
    db = DeliveryConfig.Session()

    cli = Client.sa
    mem = Member.sa
    add = Address.sa
    order = Order.sa
    oi = Order_item.sa
    comp = Component.sa
    opt = Option.sa
    co = Client_option.sa
    rest = Restriction.sa
    ri = Restricted_item.sa
    ing = Ingredient.sa
    inc = Incompatibility.sa
    ci = Component_ingredient.sa
    cai = Client_avoid_ingredient.sa
    cac = Client_avoid_component.sa

    qdainew = db.query(cli.id.label('cid'),
                       mem.firstname, mem.lastname,
                       order.id, order.delivery_date,
                       ing.name.label('ingredient'), comp.name,
                       oi.id, oi.order_id.label('oiorderid')).\
        select_from(mem).\
        join(cli, cli.member_id == mem.id).\
        join(order, order.client_id == cli.id).\
        join(cai, cai.client_id == cli.id).\
        join(ing, ing.id == cai.ingredient_id).\
        outerjoin(ci, ci.ingredient_id == ing.id).\
        outerjoin(comp, comp.id == ci.component_id).\
        outerjoin(oi, and_(oi.component_id == comp.id,
                           oi.order_id == order.id)).\
        filter(order.delivery_date == datetime.date(2016, 5, 21)).\
        order_by(cli.id)
    print_rows(qdainew,
               "\n***** Day's avoid ingredients clashes NEW ****\nCLIENT_ID,"
               "FIRSTNAME, LASTNAME, "
               "ORDER_ID, ORDER_DELIV_DATE, "
               "INGREDIENT_NAME, COMP_NAME, "
               "ORDER_ITEM_ID, ORDER_ITEM_ORDER_ID")

    qdacnew = db.query(cli.id.label('cid'),
                       mem.firstname, mem.lastname,
                       order.id, order.delivery_date,
                       comp.name.label('component'),
                       oi.id, oi.order_id.label('oiorderid')).\
        select_from(mem).\
        join(cli, cli.member_id == mem.id).\
        join(order, order.client_id == cli.id).\
        join(cac, cac.client_id == cli.id).\
        join(comp, comp.id == cac.component_id).\
        outerjoin(oi, and_(oi.component_id == comp.id,
                           oi.order_id == order.id)).\
        filter(order.delivery_date == datetime.date(2016, 5, 21)).\
        order_by(cli.id)
    print_rows(qdacnew,
               "\n***** Day's avoid component clashes NEW ****\nCLIENT_ID,"
               "FIRSTNAME, LASTNAME, "
               "ORDER_ID, ORDER_DELIV_DATE, "
               "COMP_NAME, "
               "ORDER_ITEM_ID, ORDER_ITEM_ORDER_ID")

    # No need to join with component, component_ingredient is enough
    qdcrnew = db.query(cli.id.label('cid'),
                       mem.firstname, mem.lastname,
                       order.id, order.delivery_date,
                       ri.name.label('restricted_item'),
                       ing.name.label('ingredient'), comp.name,
                       oi.id, oi.order_id.label('oiorderid')).\
        select_from(mem).\
        join(cli, cli.member_id == mem.id).\
        join(order, order.client_id == cli.id).\
        join(rest, rest.client_id == cli.id).\
        join(ri, ri.id == rest.restricted_item_id).\
        outerjoin(inc, inc.restricted_item_id == rest.restricted_item_id).\
        outerjoin(ing, inc.ingredient_id == ing.id).\
        outerjoin(ci, ci.ingredient_id == ing.id).\
        outerjoin(comp, ci.component_id == comp.id).\
        outerjoin(oi, and_(oi.component_id == comp.id,
                           oi.order_id == order.id)).\
        filter(order.delivery_date == datetime.date(2016, 5, 21)).\
        order_by(cli.id)
    print_rows(qdcrnew,
               "\n***** Day's restrictions NEW ****\nCLIENT_ID,"
               "FIRSTNAME, LASTNAME, "
               "ORDER_ID, ORDER_DELIV_DATE, "
               "RESTRICTED_ITEM, INGREDIENT_NAME, COMP_NAME, "
               "ORDER_ITEM_ID, ORDER_ITEM_ORDER_ID")

    qdpnnew = db.query(cli.id.label('cid'),
                       mem.firstname, mem.lastname,
                       opt.name.label('food_prep'),
                       order.id, order.delivery_date).\
        select_from(mem).\
        join(cli, cli.member_id == mem.id).\
        join(co, co.client_id == cli.id).\
        join(opt, opt.id == co.option_id).\
        join(order, order.client_id == cli.id).\
        filter(order.delivery_date == datetime.date(2016, 5, 21),
               opt.option_group == 'preparation').\
        order_by(mem.lastname, mem.firstname)
    print_rows(qdpnnew,
               "\n***** Day's preparations NEW****\nCLIENT_ID,"
               "FIRSTNAME, LASTNAME, "
               "FOOD_PREP, "
               "ORDER_ID, ORDER_DELIV_DATE")

    # TODO add route filter, full address, order by postal code
    qdlnnew = db.query(cli.id.label('cid'), mem.firstname, mem.lastname,
                       add.street, add.postal_code,
                       oi.total_quantity, oi.size,
                       comp.component_group).\
        select_from(mem).\
        join(cli, cli.member_id == mem.id).\
        join(add, add.id == mem.address_id).\
        join(order, order.client_id == cli.id).\
        join(oi, oi.order_id == order.id).\
        join(comp, comp.id == oi.component_id).\
        filter(order.delivery_date == datetime.date(2016, 5, 21)).\
        order_by(add.postal_code, mem.lastname, mem.firstname)
    print_rows(qdlnnew,
               "\n***** Delivery List NEW ******\n CLIENT_ID,"
               " FIRSTNAME, LASTNAME, "
               "STREET, POSTAL_CODE, "
               "OI_TOTAL_QUANTITY, OI_SIZE, "
               "COMPONENT_GROUP, ")

    # FIXME refactor Kitchen_item creation
    kitchen_list = {}
    kitchen_components = {}
    for row in qdainew.all():
        if not kitchen_list.get(row.cid):
            # found new client
            kitchen_list[row.cid] = Kitchen_item()
            kitchen_list[row.cid].lastname = row.lastname
            kitchen_list[row.cid].firstname = row.firstname
        if row.oiorderid:
            # found avoid ingredient clash
            # FIXME should be a sorted set (or ordered dict ?)
            kitchen_list[row.cid].incompatible_ingredients.append(
                row.ingredient)
        # FIXME we Know that it is not incommpatible
        elif (row.ingredient not in
              kitchen_list[row.cid].incompatible_ingredients):
            # found new other avoid ingredient that does not clash today
            # should be a set
            kitchen_list[row.cid].other_ingredients.append(
                row.ingredient)
    for row in qdacnew.all():
        if not kitchen_list.get(row.cid):
            # found new client
            kitchen_list[row.cid] = Kitchen_item()
            kitchen_list[row.cid].lastname = row.lastname
            kitchen_list[row.cid].firstname = row.firstname
        if row.oiorderid:
            # found avoid component clash
            # FIXME should be a set
            kitchen_list[row.cid].incompatible_components.append(
                row.component)
        # FIXME we Know that it is not incommpatible
        elif (row.component not in
              kitchen_list[row.cid].incompatible_components):
            # found new other avoid component that does not clash today
            # FIXME should be a set
            kitchen_list[row.cid].other_components.append(
                row.component)
    for row in qdcrnew.all():
        if not kitchen_list.get(row.cid):
            # found new client
            kitchen_list[row.cid] = Kitchen_item()
            kitchen_list[row.cid].lastname = row.lastname
            kitchen_list[row.cid].firstname = row.firstname
        if row.oiorderid:
            # found restriction clash
            # FIXME here MUST be a sorted set
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
    for row in qdpnnew.all():
        if not kitchen_list.get(row.cid):
            # found new compatible client with food preparation
            kitchen_list[row.cid] = Kitchen_item()
            kitchen_list[row.cid].lastname = row.lastname
            kitchen_list[row.cid].firstname = row.firstname
        # should be a sorted set
        kitchen_list[row.cid].preparation.append(row.food_prep)
    for row in qdlnnew.all():
        if not kitchen_list.get(row.cid):
            # found new compatible client
            #   (no avoids, no restrictions, no preparation)
            kitchen_list[row.cid] = Kitchen_item()
            kitchen_list[row.cid].lastname = row.lastname
            kitchen_list[row.cid].firstname = row.firstname
        if row.component_group == 'main dish':
            # FIXME use total_quantity
            kitchen_list[row.cid].meal_qty = kitchen_list[row.cid].meal_qty + 1
            kitchen_list[row.cid].meal_size = row.size
        kitchen_components.setdefault(row.component_group, 0)
        kitchen_components[row.component_group] = \
            kitchen_components[row.component_group] + 1

    # sort requirements list in each item
    for k, item in kitchen_list.items():
        item.incompatible_ingredients.sort()
        item.incompatible_components.sort()
        item.other_ingredients.sort()
        item.other_components.sort()
        item.restricted_items.sort()
        item.preparation.sort()

    lines = []

    lines.append(Line(incom='KCR Component Counts : ' +
                      str(kitchen_components)))
    lines.append(Line())

    total = 0
    lines.append(Line(incom='KCR list part 1 of 3 - COMPONENT CLASHING'))
    subtotal = 0
    for k, v in filter(lambda x: x[1].incompatible_components,
                       kitchen_list.items()):
        subtotal = subtotal + v.meal_qty
        lines.append(Line(client=v.lastname + ', ' + v.firstname[0:2] + '.',
                          qty=v.meal_qty, size=v.meal_size,
                          incom='clash_compo=' +
                          str(v.incompatible_components) +
                          'clash_ingre=' + str(v.incompatible_ingredients),
                          restr='avoid_compo=' + str(v.other_components) +
                          'avoid_ingre=' + str(v.other_ingredients) +
                          'restr_items=' + str(v.restricted_items),
                          prep=str(v.preparation)))
    else:
        lines.append(Line(incom='Part 1 SUBTOTAL = ' + str(subtotal)))
        total = total + subtotal
    lines.append(Line())

    lines.append(Line(incom='KCR list part 2 of 3 - INGREDIENTS CLASHING'))
    subtotal = 0
    combination = None
    for k, v in sorted(
            filter(lambda x: x[1].incompatible_ingredients,
                   kitchen_list.items()),
            key=lambda x: x[1].incompatible_ingredients):
        if combination != v.incompatible_ingredients:
            if combination:
                lines.append(Line(incom='COMBINATION ' + str(combination) +
                                  ' SUBTOTAL = ' + str(combtotal)))
            combination = v.incompatible_ingredients
            combtotal = 0
        combtotal = combtotal + v.meal_qty
        subtotal = subtotal + v.meal_qty
        lines.append(Line(client=v.lastname + ', ' + v.firstname[0:2] + '.',
                          qty=v.meal_qty, size=v.meal_size,
                          incom='clash_compo=' +
                          str(v.incompatible_components) +
                          'clash_ingre=' + str(v.incompatible_ingredients),
                          restr='avoid_compo=' + str(v.other_components) +
                          'avoid_ingre=' + str(v.other_ingredients) +
                          'restr_items=' + str(v.restricted_items),
                          prep=str(v.preparation)))
    else:
        if combination:
            lines.append(Line(incom='COMBINATION ' + str(combination) +
                              ' SUBTOTAL = ' + str(combtotal)))
            lines.append(Line(incom='Part 2 SUBTOTAL = ' + str(subtotal)))
        total = total + subtotal
    lines.append(Line())

    lines.append(Line(incom='KCR list part 3 of 3 - NO CLASHES'))
    subtotal = 0
    for k, v in sorted(
            filter(lambda x: not x[1].incompatible_ingredients,
                   kitchen_list.items()),
            key=lambda x: x[1].lastname + x[1].firstname):
        subtotal = subtotal + v.meal_qty
        lines.append(Line(client=v.lastname + ', ' + v.firstname[0:2] + '.',
                          qty=v.meal_qty, size=v.meal_size,
                          incom='clash_compo=' +
                          str(v.incompatible_components) +
                          'clash_ingre=' + str(v.incompatible_ingredients),
                          restr='avoid_compo=' + str(v.other_components) +
                          'avoid_ingre=' + str(v.other_ingredients) +
                          'restr_items=' + str(v.restricted_items),
                          prep=str(v.preparation)))
    else:
        lines.append(Line(incom='Part 3 SUBTOTAL = ' + str(subtotal)))
        total = total + subtotal
    lines.append(Line())
    lines.append(Line(incom='Parts 1,2 and 3 TOTAL = ' + str(total)))
    return render(request, 'kitchen_count.html', {'lines': lines})
