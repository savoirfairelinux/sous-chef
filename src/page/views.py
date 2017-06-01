# coding: utf-8

import collections

from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Prefetch
from django.views.generic import TemplateView
from member.models import Client, Route, Client_option, DAYS_OF_WEEK
from order.models import Order
from datetime import datetime


class HomeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'sous_chef.read'
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

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
        context['active_clients'] = active_clients
        context['pending_clients'] = pending_clients
        context['birthday'] = clients
        context['billable_orders_month'] = billable_orders
        context['billable_orders_year'] = billable_orders_year
        context['routes'] = self.calculate_route_table()
        return context

    def calculate_route_table(self):
        routes = Route.objects.prefetch_related(Prefetch(
            'client_set',
            to_attr='selected_clients',
            queryset=Client.objects.filter(
                status__in=(Client.ACTIVE, Client.PAUSED, Client.PENDING)
            ).prefetch_related(Prefetch(
                'client_option_set',
                queryset=Client_option.objects.select_related(
                    'option', 'client'
                ).filter(
                    option__name='meals_schedule'
                ).only(
                    'value', 'option__name', 'client', 'client__route'
                )
            )).only(
                'route',
                'meal_default_week',
                'delivery_type'
            )
        )).order_by('name').only('name')

        route_table = []
        for route in routes:
            defaults = collections.defaultdict(int)
            schedules = collections.defaultdict(int)
            for client in route.selected_clients:
                meals_schedule = dict(client.meals_schedule)
                meals_default = dict(client.meals_default)

                # For each day, if there's a schedule, count schedule.
                # Otherwise, count default.
                for day, _ in DAYS_OF_WEEK:
                    if day in meals_schedule:
                        schedules[day] += meals_schedule[day].get(
                            'main_dish') or 0
                    else:
                        defaults[day] += meals_default[day].get(
                            'main_dish') or 0

            route_table.append((route.name, defaults, schedules))
        return route_table


def custom_login(request):
    if request.user.is_authenticated:
        # Redirect to home if already logged in.
        return HttpResponseRedirect(reverse_lazy("page:home"))
    else:
        return login(request)
