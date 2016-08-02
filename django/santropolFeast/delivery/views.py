import datetime
import types
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from delivery.models import Delivery
from django.http import JsonResponse
from meal.factories import MenuFactory
from django.core.urlresolvers import reverse_lazy


from .apps import DeliveryConfig

from sqlalchemy import func, or_, and_

from .models import Delivery
from .forms import DateForm
from order.models import Order
from meal.models import COMPONENT_GROUP_CHOICES_MAIN_DISH, Component
from member.apps import db_session
from member.models import Client, Route
from datetime import date


class Orderlist(generic.ListView):
    # Display all the order on a given day
    model = Delivery
    template_name = 'review_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.get_orders_for_date()
        return queryset


class MealInformation(generic.ListView):
    # Display all the meal and alert for a given day
    model = Delivery
    template_name = 'ingredients.html'

    def get_context_data(self, **kwargs):

        context = super(MealInformation, self).get_context_data(**kwargs)
        context['meals'] = Component.objects.all()

        return context


class RoutesInformation(generic.ListView):
    # Display all the route information for a given day
    model = Delivery
    template_name = "routes.html"

    def get_context_data(self, **kwargs):

        context = super(RoutesInformation, self).get_context_data(**kwargs)
        context['routes'] = Route.objects.all()

        return context


# kitchen count report view and helper class and functions

class KitchenCount(generic.View):

    def get(self, request, **kwargs):
        # Display kitchen count report for given delivery date
        #   or for today by default
        if 'year' in kwargs:
            date = datetime.date(
                int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        else:
            date = datetime.date.today()
        form = DateForm(initial={'date': date})
        kitchen_list = Order.get_kitchen_items(date)
        # TODO detect if empty kitchen list
        component_lines, meal_lines = kcr_make_lines(kitchen_list, date)
        # release session for SQLAlchemy     TODO use signals instead
        db_session.remove()
        return render(request, 'kitchen_count.html',
                      {'component_lines': component_lines,
                       'meal_lines': meal_lines,
                       'form': form})

    def post(self, request):
        # change date for kitchen count report
        form = DateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            fmtdate = \
                '{:04}/{:02}/{:02}'.format(date.year, date.month, date.day)
            return HttpResponseRedirect
            ('/delivery/kitchen_count/' + fmtdate + '/')
        else:
            return render(request, 'kitchen_count.html',
                          {'component_lines': [],
                           'meal_lines': [],
                           'form': form})


class Component_line(types.SimpleNamespace):
    # line to display component count summary

    def __init__(self,
                 component_group='', rqty=0, lqty=0,
                 name='', ingredients=''):
        self.__dict__.update(
            {k: v for k, v in locals().items() if k != 'self'})


class Meal_line(types.SimpleNamespace):
    # line to display client meal specifics

    def __init__(self,
                 client='', rqty='', lqty='', comp_clash='',
                 ingr_clash='', preparation='', rest_comp='',
                 rest_ingr='', rest_item=''):
        self.__dict__.update(
            {k: v for k, v in locals().items() if k != 'self'})


def meal_line(v):
    # factory for Meal_line
    return Meal_line(
        client=v.lastname + ', ' + v.firstname[0:2] + '.',
        rqty=str(v.meal_qty) if v.meal_size == 'R' else '',
        lqty=str(v.meal_qty) if v.meal_size == 'L' else '',
        comp_clash=', '.join(v.incompatible_components),
        ingr_clash=', '.join(v.incompatible_ingredients),
        preparation=', '.join(v.preparation),
        rest_comp=', '.join(v.other_components),
        rest_ingr=', '.join(v.other_ingredients),
        rest_item=', '.join(v.restricted_items))


def kcr_cumulate(regular, large, meal):
    # count cumulative meal quantities by size

    # TODO use constant for meal size
    if meal.meal_size == 'R':
        regular = regular + meal.meal_qty
    else:
        large = large + meal.meal_qty
    return (regular, large)


def kcr_total_line(lines, label, regular, large):
    # add line to display subtotal or total quantities by size
    if regular or large:
        lines.append(
            Meal_line(client=label, rqty=str(regular), lqty=str(large)))


def kcr_make_lines(kitchen_list, date):
    # generate all the lines for the kitchen count report
    component_lines = {}
    for k, item in kitchen_list.items():
        for component_group, meal_component \
                in item.meal_components.items():
            # TODO use constant for Meal size
            component_lines.setdefault(
                component_group,
                Component_line(
                    component_group=component_group,
                    name=meal_component.name,
                    ingredients=", ".join(
                        [ing.name for ing in
                         Component.get_day_ingredients(
                             meal_component.id, date)])))
            if (component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH and
                    item.meal_size == 'L'):
                component_lines[component_group].lqty = \
                    component_lines[component_group].lqty + meal_component.qty
            else:
                component_lines[component_group].rqty = \
                    component_lines[component_group].rqty + meal_component.qty
        # END FOR
    # END FOR
    items = component_lines.items()
    if items:
        component_lines_sorted = \
            [component_lines[COMPONENT_GROUP_CHOICES_MAIN_DISH]]
        component_lines_sorted.extend(
            sorted([v for k, v in items if
                    k != COMPONENT_GROUP_CHOICES_MAIN_DISH],
                   key=lambda x: x.component_group))
    else:
        component_lines_sorted = []

    meal_lines = []
    rtotal, ltotal = (0, 0)

    # part 1 Components clashes (and other columns)
    rsubtotal, lsubtotal = (0, 0)
    for v in sorted(
            [val for val in kitchen_list.values() if
             val.incompatible_components],
            key=lambda x: x.lastname + x.firstname):
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
    # END FOR
    kcr_total_line(meal_lines, 'SUBTOTAL', rsubtotal, lsubtotal)
    rtotal, ltotal = (rtotal + rsubtotal, ltotal + lsubtotal)

    # part 2 Ingredients clashes , no components clashes (and other columns)
    rsubtotal, lsubtotal = (0, 0)
    clients = iter(sorted(
        [(ke, val) for ke, val in kitchen_list.items() if
         (val.incompatible_ingredients and
          not val.incompatible_components)],
        key=lambda x: x[1].incompatible_ingredients))
    k, v = next(clients, (0, 0))
    while k > 0:
        combination = v.incompatible_ingredients
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
        k, v = next(clients, (0, 0))
        if k == 0 or combination != v.incompatible_ingredients:
            kcr_total_line(meal_lines, 'SUBTOTAL', rsubtotal, lsubtotal)
            rtotal, ltotal = (rtotal + rsubtotal, ltotal + lsubtotal)
            rsubtotal, lsubtotal = (0, 0)
    # END WHILE

    # part 3 No clashes but preparation (and other columns)
    rsubtotal, lsubtotal = (0, 0)
    for v in sorted(
            [val for val in kitchen_list.values() if
             (not val.incompatible_ingredients and
              not val.incompatible_components and
              val.preparation)],
            key=lambda x: x.lastname + x.firstname):
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
    # END FOR
    kcr_total_line(meal_lines, 'SUBTOTAL', rsubtotal, lsubtotal)
    rtotal, ltotal = (rtotal + rsubtotal, ltotal + lsubtotal)
    kcr_total_line(meal_lines, 'TOTAL SPECIALS', rtotal, ltotal)

    rsubtotal, lsubtotal = (0, 0)
    # part 4 No clashes nor preparation but other restrictions (NOT PRINTED)
    for v in sorted(
            [val for val in kitchen_list.values() if
             (not val.incompatible_ingredients and
              not val.incompatible_components and
              not val.preparation and
              (val.other_components or
               val.other_ingredients or
               val.restricted_items))],
            key=lambda x: x.lastname + x.firstname):
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
    # END FOR

    # part 5 All columns empty (NOT PRINTED)
    for v in sorted(
            [val for val in kitchen_list.values() if
             (not val.incompatible_ingredients and
              not val.incompatible_components and
              not val.preparation and
              not val.other_components and
              not val.other_ingredients and
              not val.restricted_items)],
            key=lambda x: x.lastname + x.firstname):
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
    # END FOR
    kcr_total_line(meal_lines, 'SUBTOTAL', rsubtotal, lsubtotal)

    return (component_lines_sorted, meal_lines)


def dailyOrders(request):
    data = []
    route_id = request.GET.get('route')

    # Load all orders for the day
    orders = Order.objects.get_orders_for_date()

    for order in orders:
        if order.client.route is not None:
            if order.client.route.id == int(route_id):
                waypoint = {
                    'id': order.client.member.id,
                    'latitude': order.client.member.address.latitude,
                    'longitude': order.client.member.address.longitude,
                    'distance': order.client.member.address.distance,
                    'member': "{} {}".format(
                        order.client.member.firstname,
                        order.client.member.lastname),
                    'address': order.client.member.address.street,
                    'meal': 'meat'}
                data.append(waypoint)

    waypoints = {'waypoints': data}

    return JsonResponse(waypoints, safe=False)


@csrf_exempt
def saveRoute(request):
    members = json.loads(request.body.decode('utf-8'))

    # To do print roadmap according the list of members received

    return JsonResponse(waypoints, safe=False)


def refreshOrders(request):
    creation_date = date.today()
    delivery_date = date.today()
    clients = Client.active.all()
    MenuFactory.create(date=delivery_date)
    Order.create_orders_on_defaults(creation_date, delivery_date, clients)
    return HttpResponseRedirect(reverse_lazy("delivery:order"))
