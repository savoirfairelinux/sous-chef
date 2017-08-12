# -*- coding: utf-8 -*-

from django.conf import settings
from member.models import Client, Route
from order.models import Order, ORDER_STATUS_ORDERED
from note.models import Note, NoteFilter
import datetime


def total(request):
    """ Passing entities total into RequestContext. """

    clients = Client.objects.count()
    orders = Order.objects.count()
    routes = Route.objects.count()
    # Only unread messages
    notes = Note.unread.count()

    COMMON_CONTEXT = {
        'CLIENTS_TOTAL': clients,
        'ORDERS_TOTAL': orders,
        'ROUTES_TOTAL': routes,
        'NOTES_TOTAL': notes,
        # This is pretty bad separation of concert to puth the following here
        # But since there is no actual view associated with menu.html (it's
        # just included is base.html, this is the most DRY way I found
        'CLIENT_FILTER_DEFAULT_STATUS': Client.ACTIVE,
        'ORDER_FILTER_DEFAULT_STATUS': ORDER_STATUS_ORDERED,
        'ORDER_FILTER_DEFAULT_DATE': datetime.datetime.now(),
        'NOTE_FILTER_DEFAULT_IS_READ': NoteFilter.NOTE_STATUS_UNREAD,
        'SC_ENVIRONMENT_NAME': settings.SOUSCHEF_ENVIRONMENT_NAME,
        'SC_VERSION': settings.SOUSCHEF_VERSION,
        'GIT_HEAD': settings.GIT_HEAD,
        'GIT_TAG': settings.GIT_TAG,
    }

    return COMMON_CONTEXT
