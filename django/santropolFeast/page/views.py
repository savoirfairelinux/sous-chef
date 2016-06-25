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
from member.models import Note, Client
from datetime import datetime, timedelta
from functools import reduce
import operator


@login_required
def home(request):
    notes = list(Note.objects.all())
    active_clients = Client.objects.filter(status='A').count()
    pending_clients = Client.objects.filter(status='D').count()
    clients = Client.objects.all()
    #birthday = birthdays_within(1)
    return render(request, 'pages/home.html', {
        'notes': notes,
        'active_clients': active_clients,
        'pending_clients': pending_clients,
        'birthday': clients,
    })


def custom_login(request):
    if request.user.is_authenticated():
        # Redirect to home if already logged in.
        return HttpResponseRedirect(reverse_lazy("page:home"))
    else:
        return login(request)

def birthdays_within(days):

    now = datetime.now()
    then = now + timedelta(days)

    # Build the list of month/day tuples.
    monthdays = [(now.month, now.day)]
    while now <= then:
        monthdays.append((now.month, now.day))
        now += timedelta(days=1)

    # Tranform each into queryset keyword args.
    monthdays = (dict(zip(("birthdate__month", "birthdate__day"), t))
                 for t in monthdays)


    # Compose the djano.db.models.Q objects together for a single query.
    query = reduce(operator.or_, (Client(**d) for d in monthdays))

    # Run the query.
    return Client.objects.filter(query)
