# -*- coding: utf-8 -*-

from member.models import Client
from order.models import Order, ORDER_STATUS_ORDERED
from note.models import Note, NoteFilter
import datetime


def total(request):
    """ Passing entities total into RequestContext. """

    clients = Client.objects.count()
    orders = Order.objects.count()
    # Only unread messages
    notes = Note.unread.count()

    COMMON_CONTEXT = {
        'CLIENTS_TOTAL': clients,
        'ORDERS_TOTAL': orders,
        'NOTES_TOTAL': notes,
        # This is pretty bad separation of concert to puth the following here
        # But since there is no actual view associated with menu.html (it's
        # just included is base.html, this is the most DRY way I found
        'CLIENT_FILTER_DEFAULT_STATUS': Client.ACTIVE,
        'ORDER_FILTER_DEFAULT_STATUS': ORDER_STATUS_ORDERED,
        'ORDER_FILTER_DEFAULT_DATE': datetime.datetime.now(),
        'NOTE_FILTER_DEFAULT_IS_READ': NoteFilter.NOTE_STATUS_UNREAD
        
    }

    return COMMON_CONTEXT
