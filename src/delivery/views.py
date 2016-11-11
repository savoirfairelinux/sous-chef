import collections
import datetime
from datetime import date
import json
import os
import textwrap
import types

from django.conf import settings
from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.http import JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.contrib.admin.models import LogEntry, ADDITION
from django.db.models.functions import Lower

import labels  # package pylabels
from reportlab.graphics import shapes

from delivery.models import Delivery
from meal.models import (
    COMPONENT_GROUP_CHOICES, COMPONENT_GROUP_CHOICES_MAIN_DISH,
    Component,
    Menu, Menu_component,
    Component_ingredient)
from member.models import Client, Route
from order.models import (
    Order, component_group_sorting, SIZE_CHOICES_REGULAR, SIZE_CHOICES_LARGE)
from .models import Delivery
from .forms import DishIngredientsForm
from . import tsp

MEAL_LABELS_FILE = os.path.join(settings.BASE_DIR, "meallabels.pdf")
DELIVERY_STARTING_POINT_LAT_LONG = (45.516564, -73.575145)  # Santropol Roulant


class Orderlist(generic.ListView):
    # Display all the order on a given day
    model = Delivery
    template_name = 'review_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.get_shippable_orders()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(Orderlist, self).get_context_data(**kwargs)
        context['orders_refresh_date'] = None
        if LogEntry.objects.exists():
            log = LogEntry.objects.latest('action_time')
            context['orders_refresh_date'] = log

        return context


class MealInformation(generic.View):
    # Choose today's main dish and its ingredients

    def get(self, request, **kwargs):
        # Display today's main dish and its ingredients

        date = datetime.date.today()
        main_dishes = Component.objects.order_by(Lower('name')).filter(
            component_group=COMPONENT_GROUP_CHOICES_MAIN_DISH)
        if 'id' in kwargs:
            # today's main dish has been chosen by user
            main_dish = Component.objects.get(id=int(kwargs['id']))
            # delete existing ingredients for the date + dish
            Component_ingredient.objects.filter(
                component=main_dish, date=date).delete()
        else:
            # see if a menu exists for today
            menu_comps = Menu_component.objects.filter(
                menu__date=date,
                component__component_group=COMPONENT_GROUP_CHOICES_MAIN_DISH)
            if menu_comps:
                # main dish is known in today's menu
                main_dish = menu_comps[0].component
            else:
                # take first main dish
                main_dish = main_dishes[0]

        # see if existing chosen ingredients for the dish
        dish_ingredients = Component.get_day_ingredients(
            main_dish.id, date)
        if not dish_ingredients:
            # get recipe ingredients for the dish
            dish_ingredients = Component.get_recipe_ingredients(
                main_dish.id)

        form = DishIngredientsForm(
            initial={
                'maindish': main_dish.id,
                'ingredients': dish_ingredients})

        return render(
            request,
            'ingredients.html',
            {'form': form,
             'date': str(date)})

    def post(self, request):
        # Choose ingredients in today's main dish

        # print("Pick Ingredients POST request=", request.POST)  # For testing
        date = datetime.date.today()
        form = DishIngredientsForm(request.POST)
        if '_restore' in request.POST:
            # restore ingredients of main dish to those in recipe
            if form.is_valid():
                component = form.cleaned_data['maindish']
                # delete existing ingredients for the date + dish
                Component_ingredient.objects.filter(
                    component=component, date=date).delete()
                return HttpResponseRedirect(
                    reverse_lazy("delivery:meal_id", args=[component.id]))
        elif '_next' in request.POST:
            # forward to kitchen count
            if form.is_valid():
                ingredients = form.cleaned_data['ingredients']
                component = form.cleaned_data['maindish']
                # delete existing ingredients for the date + dish
                Component_ingredient.objects.filter(
                    component=component, date=date).delete()
                # add revised ingredients for the date + dish
                for ing in ingredients:
                    ci = Component_ingredient(
                        component=component,
                        ingredient=ing,
                        date=date)
                    ci.save()
                # END FOR
                # Create menu and its components for today
                compnames = [component.name]  # main dish
                # take first sorted name of each other component group
                for group, ignore in COMPONENT_GROUP_CHOICES:
                    if group != COMPONENT_GROUP_CHOICES_MAIN_DISH:
                        compname = Component.objects.order_by(
                            Lower('name')).filter(
                                component_group=group
                            )
                        if compname:
                            compnames.append(compname[0].name)
                Menu.create_menu_and_components(date, compnames)
                return HttpResponseRedirect(
                    reverse_lazy("delivery:kitchen_count"))
            # END IF
        # END IF
        return render(
            request,
            'ingredients.html',
            {'date': date,
             'form': form})

class RouteInformation(generic.ListView):
    # Display all the route information for a given day
    model = Delivery
    template_name = "route.html"

    def get_context_data(self, **kwargs):

        context = super(RouteInformation, self).get_context_data(**kwargs)
        context['routes'] = Route.objects.all()

        return context


class RoutesInformation(generic.ListView):
    # Display all the route information for a given day
    model = Delivery
    template_name = "routes.html"

    def get_context_data(self, **kwargs):

        context = super(RoutesInformation, self).get_context_data(**kwargs)
        routes = Route.objects.all()
        orders = []
        for route in routes:
            orders.append((route, Order.objects.get_shippable_orders_by_route(route.id).count()))
        context['routes'] = orders

        return context


class OrganizeRoute(generic.ListView):
    # Display all the route information for a given day
    model = Delivery
    template_name = "organize_route.html"

    def get_context_data(self, **kwargs):

        context = super(OrganizeRoute, self).get_context_data(**kwargs)
        context['route'] = Route.objects.get(id=self.kwargs['id'])

        return context



# Kitchen count report view, helper classes and functions

class KitchenCount(generic.View):

    def get(self, request, **kwargs):
        # Display kitchen count report for given delivery date
        #   or for today by default; generate meal labels
        if 'year' in kwargs and 'month' in kwargs and 'day' in kwargs:
            date = datetime.date(
                int(kwargs['year']), int(kwargs['month']), int(kwargs['day']))
        else:
            date = datetime.date.today()

        kitchen_list = Order.get_kitchen_items(date)
        component_lines, meal_lines = kcr_make_lines(kitchen_list, date)
        num_labels = kcr_make_labels(kitchen_list)
        return render(request, 'kitchen_count.html',
                      {'component_lines': component_lines,
                       'meal_lines': meal_lines,
                       'num_labels': num_labels})


component_line_fields = [          # Component summary Line on Kitchen Count.
    # field name       default value
    'component_group', '',    # ex. main dish, dessert etc
    'rqty',            0,     # Quantity of regular size main dishes
    'lqty',            0,     # Quantity of large size main dishes
    'name',            '',    # String : component name
    'ingredients'      '']    # String : today's ingredients in main dish
ComponentLine = collections.namedtuple(
    'ComponentLine', component_line_fields[0::2])


meal_line_fields = [               # Special Meal Line on Kitchen Count.
    # field name       default value
    'client',          '',     # String : Lastname and abbreviated first name
    'rqty',            '',     # String : Quantity of regular size main dishes
    'lqty',            '',     # String : Quantity of large size main dishes
    'ingr_clash',      '',     # String : Ingredients that clash
    'preparation',     '',     # String : Meal preparations
    'rest_ingr',       '',     # String : Other ingredients to avoid
    'rest_item',       '',     # String : Restricted items
    'span',            None]   # Number of lines to "rowspan" in table
MealLine = collections.namedtuple(
    'MealLine', meal_line_fields[0::2])


def meal_line(kititm):
    """Builds a line for the main section of the Kitchen Count Report.

    Given a client's special requirements, assemble the fields of a line
    that will be displayed / printed in the Kitchen Count Report.

    Args:
        kititm : A KitchenItem object (see order/models)

    Returns:
        A MealLine object
    """
    return MealLine(
        client=kititm.lastname + ', ' + kititm.firstname[0:2] + '.',
        rqty=(str(kititm.meal_qty)
              if kititm.meal_size == SIZE_CHOICES_REGULAR else ''),
        lqty=(str(kititm.meal_qty)
              if kititm.meal_size == SIZE_CHOICES_LARGE else ''),
        ingr_clash=', '.join(kititm.incompatible_ingredients),
        preparation=', '.join(kititm.preparation),
        rest_ingr=', '.join(kititm.other_ingredients),
        rest_item=', '.join(kititm.restricted_items),
        span=None)


def kcr_cumulate(regular, large, meal):
    """Count cumulative meal quantities by size.

    Based on the size and on the number of servings of the 'meal',
    calculate the new cumulative quantities by size.

    Args:
        regular : carried over quantity of regular size main dishes.
        large : carried over quantity of large size main dishes.
        meal : MealLine object

    Returns:
        A tuple of the new cumulative quantities : (regular, large)
    """
    if meal.meal_size == SIZE_CHOICES_REGULAR:
        regular = regular + meal.meal_qty
    else:
        large = large + meal.meal_qty
    return (regular, large)


def kcr_make_lines(kitchen_list, date):
    """Generate the sections and lines for the kitchen count report.

    Count all the dishes that have to be prepared and identify all the
    special client requirements such as disliked ingredients,
    restrictions and necessary food preparation.

    Args: kitchen_list : A dictionary of KitchenItem objects (see
              order/models) which contain detailed information about
              all the meals that have to be prepared for the day and
              the client requirements and restrictions.
          date : A date.datetime object giving the date on which the
              meals will be delivered.

    Returns:
        A tuple. First value is the component (dishes) summary lines. The
          second value is the special meals lines.
    """
    # Build component summary
    component_lines = {}
    for k, item in kitchen_list.items():
        for component_group, meal_component \
                in item.meal_components.items():
            component_lines.setdefault(
                component_group,
                ComponentLine(
                    component_group=component_group,
                    rqty=0,
                    lqty=0,
                    name=meal_component.name,
                    ingredients=", ".join(
                        [ing.name for ing in
                         Component.get_day_ingredients(
                             meal_component.id, date)])))
            if (component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH and
                    item.meal_size == SIZE_CHOICES_LARGE):
                component_lines[component_group] = \
                    component_lines[component_group]._replace(
                        lqty=(component_lines[component_group].lqty +
                              meal_component.qty))
            else:
                component_lines[component_group] = \
                    component_lines[component_group]._replace(
                        rqty=(component_lines[component_group].rqty +
                              meal_component.qty))
        # END FOR
    # END FOR
    # Sort component summary
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

    # Build special meal lines

    meal_lines = []
    rtotal, ltotal = (0, 0)
    # part 1 Ingredients clashes (and other columns)
    rsubtotal, lsubtotal = (0, 0)
    clients = iter(sorted(
        [(ke, val) for ke, val in kitchen_list.items() if
         val.incompatible_ingredients],
        key=lambda x: x[1].incompatible_ingredients))
    # first line of a combination of ingredients
    line_start = len(meal_lines)
    k, v = next(clients, (0, 0))
    while k > 0:
        combination = v.incompatible_ingredients
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
        k, v = next(clients, (0, 0))
        if k == 0 or combination != v.incompatible_ingredients:
            meal_lines.append(MealLine(*meal_line_fields[1::2])._replace(
                client='SUBTOTAL', rqty=str(rsubtotal), lqty=str(lsubtotal)))
            rtotal, ltotal = (rtotal + rsubtotal, ltotal + lsubtotal)
            rsubtotal, lsubtotal = (0, 0)
            # last line of this combination of ingredients
            line_end = len(meal_lines)
            # set rowspan to total number of lines for this combination
            meal_lines[line_start] = meal_lines[line_start]._replace(
                span=str(line_end - line_start))
            # hide ingredients for lines following the first
            for j in range(line_start + 1, line_end):
                meal_lines[j] = meal_lines[j]._replace(span='-1')
            # Add a blank line as separator
            meal_lines.append(MealLine(*meal_line_fields[1::2]))
            # first line of next combination of ingredients
            line_start = len(meal_lines)
    # END WHILE

    # part 2 No clashes but preparation (and other columns)
    rsubtotal, lsubtotal = (0, 0)
    for v in sorted(
            [val for val in kitchen_list.values() if
             (not val.incompatible_ingredients and
              val.preparation)],
            key=lambda x: x.lastname + x.firstname):
        meal_lines.append(meal_line(v))
        rsubtotal, lsubtotal = kcr_cumulate(rsubtotal, lsubtotal, v)
        # Add a blank line as separator
        meal_lines.append(MealLine(*meal_line_fields[1::2]))
    # END FOR
    if rsubtotal or lsubtotal:
        meal_lines.append(MealLine(*meal_line_fields[1::2])._replace(
            client='SUBTOTAL', rqty=str(rsubtotal), lqty=str(lsubtotal)))
    rtotal, ltotal = (rtotal + rsubtotal, ltotal + lsubtotal)
    meal_lines.append(MealLine(*meal_line_fields[1::2])._replace(
        rqty=str(rtotal), lqty=str(ltotal), ingr_clash='TOTAL SPECIALS'))

    return (component_lines_sorted, meal_lines)


def kcr_make_labels(kitchen_list):
    """Generate Meal Labels sheets as a PDF file.

    Generate a label for each main dish serving to be delivered. The
    sheet format is "Avery 5162" 8,5 X 11 inches, 2 cols X 7 lines.

    Uses pylabels package - see https://github.com/bcbnz/pylabels
    and ReportLab

    Args: kitchen_list : A dictionary of KitchenItem objects (see
              order/models) which contain detailed information about
              all the meals that have to be prepared for the day and
              the client requirements and restrictions.

    Returns:
        An integer : The number of labels generated.
    """
    # dimensions are in millimeters; 1 inch = 25.4 mm
    specs = labels.Specification(
        sheet_width=8.5 * 25.4, sheet_height=11 * 25.4,
        columns=2, rows=7,
        label_width=4 * 25.4, label_height=1.33 * 25.4,
        top_margin=20, bottom_margin=20,
        corner_radius=2)

    def draw_label(label, width, height, data):
        # callback function
        obj, j, qty = data
        label.add(shapes.String(2, height * 0.8,
                                obj.lastname + ", " + obj.firstname[0:2] + ".",
                                fontName="Helvetica-Bold",
                                fontSize=12))
        label.add(shapes.String(width-2, height * 0.8,
                                "{}".format(datetime.date.today().
                                            strftime("%a, %b-%d")),
                                fontName="Helvetica",
                                fontSize=10,
                                textAnchor="end"))
        if obj.meal_size == SIZE_CHOICES_LARGE:
            label.add(shapes.String(2, height * 0.65,
                                    "LARGE",
                                    fontName="Helvetica",
                                    fontSize=10))
        if qty > 1:
            label.add(shapes.String(width * 0.5, height * 0.65,
                                    "(" + str(j) + " of " + str(qty) + ")",
                                    fontName="Helvetica",
                                    fontSize=10))
        label.add(shapes.String(width-3, height * 0.65,
                                obj.routename,
                                fontName="Helvetica-Oblique",
                                fontSize=8,
                                textAnchor="end"))

        special = []
        special.extend(obj.preparation)
        special.extend(["No " + item for item in obj.incompatible_ingredients])
        special.extend(["No " + item for item in obj.other_ingredients])
        special.extend(["No " + item for item in obj.restricted_items])
        special = textwrap.wrap(
            ' / '.join(special), width=68,
            break_long_words=False, break_on_hyphens=False)
        position = height * 0.45
        for line in special:
            label.add(shapes.String(2, position,
                                    line,
                                    fontName="Helvetica",
                                    fontSize=9))
            position -= 10
    # END DEF

    sheet = labels.Sheet(specs, draw_label, border=True)

    # obj is a KitchenItem instance (see order/models.py)
    for obj in sorted(
            list(kitchen_list.values()),
            key=lambda x: x.lastname + x.firstname):
        qty = obj.meal_qty
        for j in range(1, qty + 1):
            sheet.add_label((obj, j, qty))

    if sheet.label_count > 0:
        sheet.save(MEAL_LABELS_FILE)
    return sheet.label_count

# END Kitchen count report view, helper classes and functions

# Delivery route sheet view, helper classes and functions


class MealLabels(generic.View):

    def get(self, request, **kwargs):
        try:
            f = open(MEAL_LABELS_FILE, "rb")
        except:
            raise Http404("File " + MEAL_LABELS_FILE + " does not exist")
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = \
            'attachment; filename="labels{}.pdf"'. \
            format(datetime.date.today().strftime("%Y%m%d"))
        response.write(f.read())
        f.close()
        return response


class DeliveryRouteSheet(generic.View):

    def get(self, request, **kwargs):
        # Display today's delivery sheet for given route
        route_id = int(kwargs['id'])
        date = datetime.date.today()

        route = Route.objects.get(id=route_id)
        # date_stored is not used here
        date_stored, route_client_ids = route.get_client_sequence()
        route_list = Order.get_delivery_list(date, route_id)
        route_list = sort_sequence_ids(route_list, route_client_ids)
        summary_lines, detail_lines = drs_make_lines(route_list, date)
        return render(request, 'route_sheet.html',
                      {'route': route,
                       'summary_lines': summary_lines,
                       'detail_lines': detail_lines})


RouteSummaryLine = \
    collections.namedtuple(
        'RouteSummaryLine',
        ['component_group',
         'rqty',
         'lqty'])


def drs_make_lines(route_list, date):
    # generate all the lines for the delivery route sheet

    summary_lines = {}
    for k, item in route_list.items():
        # print("\nitem = ", item)
        for delivery_item in item.delivery_items:
            component_group = delivery_item.component_group
            if component_group:
                line = summary_lines.setdefault(
                    component_group,
                    RouteSummaryLine(
                        component_group,
                        rqty=0,
                        lqty=0))
                # print("\nline", line)
                if (component_group == COMPONENT_GROUP_CHOICES_MAIN_DISH and
                        delivery_item.size == SIZE_CHOICES_LARGE):
                    summary_lines[component_group] = \
                        line._replace(lqty=line.lqty +
                                      delivery_item.total_quantity)
                elif component_group != '':
                    summary_lines[component_group] = \
                        line._replace(rqty=line.rqty +
                                      delivery_item.total_quantity)
                # END IF
            # END IF
        # END FOR
    # END FOR

    # print("values before sort", summary_lines.values())
    summary_lines_sorted = sorted(
        summary_lines.values(),
        key=component_group_sorting)
    # print("values after sort", summary_lines_sorted)
    return summary_lines_sorted, list(route_list.values())


def sort_sequence_ids(unordered_dic, seq):
    """Sort items in a dictionary according to a sequence of keys.

    Build an ordered dictionary using ordering of keys in 'seq' but
    ignoring the keys in 'seq' that are not in 'unordered_dic'.

    Args:
        unordered_dic : dictionary for which some keys may be absent from 'seq'
        seq : list of keys that may not all be entries in 'dic'

    Returns:
        A ordered dictionary : collections.OrderedDict()
    """
    od = collections.OrderedDict()
    if seq:
        for k in seq:
            if unordered_dic.get(k):
                od[k] = None
    # place all values from unordered_dic into ordered dict;
    #   keys not in seq will be added at the end.
    for k, val in unordered_dic.items():
        od[k] = val
    return od

# END Delivery route sheet view, helper classes and functions


def calculateRoutePointsEuclidean(data):
    """Find shortest path for points on route assuming 2D plane.

    Since the
    https://www.mapbox.com/api-documentation/#retrieve-a-duration-matrix
    endpoint is not yet available, we solve an approximation of the
    problem by assuming the world is flat and has no obstacles (2D
    Euclidean plane). This should still give good results.

    Args:
        data : A list of waypoints for leaflet.js

    Returns:
        An optimized list of waypoints.
    """
    node_to_waypoint = {}
    nodes = [tsp.Node(None,
                      DELIVERY_STARTING_POINT_LAT_LONG[0],
                      DELIVERY_STARTING_POINT_LAT_LONG[1])]
    for waypoint in data:
        node = tsp.Node(waypoint['id'], float(waypoint['latitude']),
                        float(waypoint['longitude']))
        node_to_waypoint[node] = waypoint
        nodes.append(node)
    # Optimize waypoints by solving the Travelling Salesman Problem
    nodes = tsp.solve(nodes)
    # Guard against starting point which is not in node_to_waypoint
    return [node_to_waypoint[node] for
            node in nodes if node in node_to_waypoint]


def retrieveRoutePoints(route_id, data):
    """Attempt to sort a route according to previously saved points.

    If we find a sequence of client ids saved for the route having 'route_id',
    sort the list of waypoints in 'data' accordingly.

    Args:
        route_id : The id of a delivery route.
        data : A list of waypoints for leaflet.js

    Returns:
        A list of waypoints.
    """
    route = Route.objects.get(id=route_id)
    # date_stored is not used here
    date_stored, route_client_ids = route.get_client_sequence()
    if route_client_ids:
        # sort waypoints according to previously saved route
        member_ids = \
            [Client.objects.get(id=cid).member.id
             for cid in route_client_ids]
        unsorted_dic = {waypoint['id']: waypoint for waypoint in data}
        sorted_dic = sort_sequence_ids(unsorted_dic, member_ids)
        return list(sorted_dic.values())
    else:
        # no saved route found, return unsorted points
        return data


def dailyOrders(request):
    """Get the sequence of points for a delivery route.

    Args:
        request : an http request having parameters 'route' and 'mode'.

    Returns:
        A json response containing waypoints for leaflet.js.
    """
    data = []
    route_id = request.GET.get('route')
    # mode is one of :
    #   'euclidean' to calculate shortest path of points assuming
    #      a 2D euclidean plane for the TSP algorithm
    #   'retrieve' to sort points according to previously saved sequence
    #   'cycling' : shortest path using mapbox durations NOT YET IMPLEMENTED
    #   'driving' : shortest path using mapbox durations NOT YET IMPLEMENTED
    #   'walking' : shortest path using mapbox durations NOT YET IMPLEMENTED
    mode = request.GET.get('mode')
    # Load all orders for the day
    orders = Order.objects.get_shippable_orders()

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
                    'address': order.client.member.address.street
                    }
                data.append(waypoint)

    if mode == 'euclidean':
        data = calculateRoutePointsEuclidean(data)
    elif mode == 'retrieve':
        data = retrieveRoutePoints(route_id, data)
    else:
        # unknown mode
        raise Exception(
            "delivery dailyOrders mode '{}' unknown".format(mode))

    waypoints = {'waypoints': data}

    return JsonResponse(waypoints, safe=False)


@csrf_exempt
def saveRoute(request):
    """Save the sequence of points for a delivery route.

    Saves a sequence of client ids for the delivery route.

    Args:
        request : an http request having parameters 'members' and 'route'.

    Returns:
        A json response confirming success.
    """
    data = json.loads(request.body.decode('utf-8'))
    member_ids = [member['id'] for member in data['members']]
    route_id = data['route'][0]['id']
    route_client_ids = \
        [Client.objects.get(member__id=member_id).id
         for member_id in member_ids]
    route = Route.objects.get(id=route_id)
    route.set_client_sequence(datetime.date.today(), route_client_ids)
    route.save()
    return JsonResponse('OK', safe=False)


def refreshOrders(request):
    delivery_date = date.today()
    last_refresh_date = datetime.datetime.now()
    clients = Client.active.all()
    Order.objects.auto_create_orders(delivery_date, clients)
    LogEntry.objects.log_action(
        user_id=1, content_type_id=1,
        object_id="", object_repr="Generation of order for " + str(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M')),
        action_flag=ADDITION,
    )
    return HttpResponseRedirect(reverse_lazy("delivery:order"))
