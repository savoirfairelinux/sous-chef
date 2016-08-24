# -*- coding: utf-8 -*-

from member.models import Client
from order.models import Order
from note.models import Note


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
    }

    return COMMON_CONTEXT
