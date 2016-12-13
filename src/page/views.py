# coding: utf-8

from django.contrib.auth import logout
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from member.models import Client
from order.models import Order
from datetime import datetime, timedelta
from functools import reduce
import operator


@login_required
def home(request):
    today = datetime.today()
    active_clients = Client.active.all().count()
    pending_clients = Client.pending.all().count()
    clients = Client.contact.get_birthday_boys_and_girls()
    billable_orders = Order.objects.get_billable_orders(
        today.year, today.month
    ).count()
    billable_orders_year = Order.objects.filter(
        status='D',
        delivery_date__year=datetime.today().year).count()
    return render(request, 'pages/home.html', {
        'active_clients': active_clients,
        'pending_clients': pending_clients,
        'birthday': clients,
        'billable_orders_month': billable_orders,
        'billable_orders_year': billable_orders_year
    })


def custom_login(request):
    if request.user.is_authenticated():
        # Redirect to home if already logged in.
        return HttpResponseRedirect(reverse_lazy("page:home"))
    else:
        return login(request)
