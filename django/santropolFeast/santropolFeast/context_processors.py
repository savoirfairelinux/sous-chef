# -*- coding: utf-8 -*-

from member.models import Client
from order.models import Order
from meal.models import Ingredient

def total(request):
    """ Passing entities total into RequestContext. """

    clients = Client.objects.count()
    orders = Order.objects.count()
    ingredients = Ingredient.objects.count()

    COMMON_CONTEXT = {
        'CLIENTS_TOTAL': clients,
        'ORDERS_TOTAL': orders,
        'INGREDIENTS_TOTAL': ingredients,
    }

    return COMMON_CONTEXT
