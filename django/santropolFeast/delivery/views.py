import datetime
import types
from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from delivery.models import Delivery
from django.http import JsonResponse
from meal.factories import MenuFactory
from django.core.urlresolvers import reverse_lazy


from .apps import DeliveryConfig

from sqlalchemy import func, or_, and_

from .models import Delivery
from .forms import DateForm, DayIngredientsForm
from order.models import Order
from meal.models import (
    COMPONENT_GROUP_CHOICES_MAIN_DISH, Component, Ingredient, Menu_component,
    Component_ingredient)
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


class MealInformation(generic.View):

    def get(self, request, **kwargs):
        # Choose ingredients for given delivery date
        #   or for today by default
        if 'year' in kwargs and 'month' in kwargs and 'day' in kwargs:
            date = datetime.date(
                int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        else:
            date = datetime.date.today()
        date_form = DateForm(initial={'date': date})
        # TODO use managers
        main_dishes = Menu_component.objects.filter(
            menu__date=date,
            component__component_group=COMPONENT_GROUP_CHOICES_MAIN_DISH)
        if main_dishes:
            main_dish_name = main_dishes[0].component.name
            # get existing ingredients for the date + dish, if any
            dish_ingredients = Component.get_day_ingredients(
                    main_dishes[0].component.id, date)
            if not dish_ingredients:
                # get recipe ingredients for the dish
                dish_ingredients = Component.get_recipe_ingredients(
                    main_dishes[0].component.id)
            all_ingredients = \
                [ingredient.name for ingredient in Ingredient.objects.all()]
            ing_form = DayIngredientsForm(
                choices=[(a, a) for a in all_ingredients],
                initial={'ingredients': dish_ingredients,
                         'date': date,
                         'dish': main_dish_name})
        else:
            main_dish_name = 'None for chosen date'
            ing_form = DayIngredientsForm(choices=[])
        return render(
            request,
            'ingredients.html',
            {'date_form': date_form,
             'date': str(date),
             'main_dish_name': main_dish_name,
             'ing_form': ing_form})

    def post(self, request):
        date_form = None
        ing_form = None
        main_dish_name = ''
        # print("post request", request.POST)  # debug
        if '_change' in request.POST:
            # change date for day's ingredients
            date_form = DateForm(request.POST)
            if date_form.is_valid():
                date = date_form.cleaned_data['date']
                fmtdate = \
                    '{:04}/{:02}/{:02}'.format(date.year, date.month, date.day)
                return HttpResponseRedirect('/delivery/meal/' + fmtdate + '/')
        elif '_back' in request.POST:
            # back to order step
            return HttpResponseRedirect('/delivery/order/')
        elif '_next' in request.POST:
            # forward to kitchen count
            all_ingredients = \
                [ingredient.name for ingredient in Ingredient.objects.all()]
            ing_form = DayIngredientsForm(
                request.POST, choices=[(a, a) for a in all_ingredients])
            if ing_form.is_valid():
                ingredients = ing_form.cleaned_data['ingredients']
                date = ing_form.cleaned_data['date']
                main_dish_name = ing_form.cleaned_data['dish']
                component = Component.objects.get(name=main_dish_name)
                # delete existing ingredients for the date + dish
                Component_ingredient.objects.filter(
                    component=component, date=date).delete()
                # add revised ingredients for the date + dish
                for ing in Ingredient.objects.filter(name__in=ingredients):
                    ci = Component_ingredient(
                        component=component,
                        ingredient=ing,
                        date=date)
                    ci.save()
                    # print("ci=", ci)  # DEBUG
                fmtdate = \
                    '{:04}/{:02}/{:02}'.format(date.year, date.month, date.day)
                return HttpResponseRedirect(
                    '/delivery/kitchen_count/' + fmtdate + '/')
                # END FOR
            # END IF
        # END IF
        if not date_form:
            date_form = DateForm(request.POST)
        if not ing_form:
            ing_form = DayIngredientsForm(choices=[])
        return render(
            request,
            'ingredients.html',
            {'date_form': date_form,
             'date': '',
             'main_dish_name': main_dish_name,
             'ing_form': ing_form})


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
        if 'year' in kwargs and 'month' in kwargs and 'day' in kwargs:
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
            return HttpResponseRedirect(
                '/delivery/kitchen_count/' + fmtdate + '/')
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

    # Load all orders for the day
    orders = Order.objects.get_orders_for_date()

    data = []

    for order in orders:
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


def routeDailyOrders(request):
    # do something with the your data

    data = {'waypoints': [
        {'latitude': 45.5165, 'longitude': -73.567,
            'member': 'toto', 'meal': 'meat'},
        {'latitude': 45.548664, 'longitude': -73.681145,
            'member': 'tata', 'meal': 'vegie'},
        {'latitude': 45.558664, 'longitude': -
            73.685945, 'member': 'titi', 'meal': 'meat'}
    ]
    }

    # just return a JsonResponse
    return JsonResponse(data)


def refreshOrders(request):
    creation_date = date.today()
    delivery_date = date.today()
    clients = Client.active.all()
    MenuFactory.create(date=delivery_date)
    Order.create_orders_on_defaults(creation_date, delivery_date, clients)
    return HttpResponseRedirect(reverse_lazy("delivery:order"))
