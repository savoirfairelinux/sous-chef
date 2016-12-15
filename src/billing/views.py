import copy
import collections

from django.shortcuts import render
from django.db.models import Q
from django.views import generic
from django.utils.translation import string_concat
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from billing.models import (
    Billing, calculate_amount_total, BillingFilter
)
from order.models import DeliveredOrdersByMonth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from order.models import Order, Order_item
from django.http import HttpResponseRedirect
from member.models import Client


class BillingList(generic.ListView):
    # Display the billing list
    model = Billing
    template_name = "billing/list.html"
    context_object_name = "billings"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingList, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BillingList, self).get_context_data(**kwargs)
        uf = BillingFilter(self.request.GET, queryset=self.get_queryset())
        context['filter'] = uf

        return context

    def get_queryset(self):
        uf = BillingFilter(self.request.GET)
        return uf.qs


class BillingCreate(generic.CreateView):
    # View to create the billing
    model = Billing
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingCreate, self).dispatch(*args, **kwargs)

    def get(self, request):
        date = self.request.GET.get('delivery_date', '')
        year, month = date.split('-')

        if year is '' or month is '':
            return HttpResponseRedirect(reverse_lazy('billing:list'))

        billing = Billing.objects.billing_create_new(year, month)

        messages.add_message(
            self.request, messages.SUCCESS,
            _("The billing with the identifier #%s \
            has been successfully created." % billing.id)
        )
        return HttpResponseRedirect(reverse_lazy('billing:list'))


class BillingAdd(generic.ListView):
    model = Order
    template_name = "billing/add.html"
    context_object_name = "orders"
    paginate_by = 20

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingAdd, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BillingAdd, self).get_context_data(**kwargs)
        uf = DeliveredOrdersByMonth(
            self.request.GET, queryset=self.get_queryset())
        context['filter'] = uf
        text = ''
        count = 0
        for getVariable in self.request.GET:
            if getVariable == "page":
                continue
            for getValue in self.request.GET.getlist(getVariable):
                if count == 0:
                    text += "?" + getVariable + "=" + getValue
                else:
                    text += "&" + getVariable + "=" + getValue
                count += 1

        text = text + "?" if count == 0 else text + "&"
        context['get'] = text

        return context

    def get_queryset(self):
        uf = DeliveredOrdersByMonth(self.request.GET)
        return uf.qs


class BillingSummaryView(generic.DetailView):
    # Display summary of billing
    model = Billing
    template_name = "billing/view.html"
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingSummaryView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        if self.request.method == "GET" and \
           self.request.GET.get('print'):
            return ['billing/print_summary.html']
        else:
            return super(BillingSummaryView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(BillingSummaryView, self).get_context_data(**kwargs)
        billing = self.object

        # generate a summary
        zero_statistics = {
            'total_main_dishes': {
                'R': 0,
                'L': 0
            },
            'total_billable_sides': 0,
            'total_amount': 0
        }
        # target dict
        summary = copy.deepcopy(zero_statistics)
        summary['payment_types_dict'] = collections.defaultdict(
            lambda: dict(clients=[], **copy.deepcopy(zero_statistics))
        )
        for client, client_summary in billing.summary.items():
            t = client.billing_payment_type
            summary['payment_types_dict'][t]['total_main_dishes']['R'] += (
                client_summary['total_main_dishes']['R']
            )
            summary['payment_types_dict'][t]['total_main_dishes']['L'] += (
                client_summary['total_main_dishes']['L']
            )
            summary['payment_types_dict'][t]['total_billable_sides'] += (
                client_summary['total_billable_sides']
            )
            summary['payment_types_dict'][t]['total_amount'] += (
                client_summary['total_amount']
            )
            summary['payment_types_dict'][t]['clients'].append({
                'id': client.id,
                'firstname': client.member.firstname,
                'lastname': client.member.lastname,
                'payment_type': client.get_billing_payment_type_display(),
                'rate_type': client.get_rate_type_display() if (
                    client.rate_type != 'default') else '',
                'total_main_dishes': client_summary['total_main_dishes'],
                'total_billable_sides': client_summary['total_billable_sides'],
                'total_amount': client_summary['total_amount']
            })
            summary['total_main_dishes']['R'] += (
                client_summary['total_main_dishes']['R']
            )
            summary['total_main_dishes']['L'] += (
                client_summary['total_main_dishes']['L']
            )
            summary['total_billable_sides'] += (
                client_summary['total_billable_sides']
            )
            summary['total_amount'] += (
                client_summary['total_amount']
            )
        for payment_type, statistics in summary['payment_types_dict'].items():
            statistics['clients'].sort(
                key=lambda c: (c['lastname'], c['firstname'])
            )
        import pprint
        pprint.pprint(summary, indent=4)
        # define the order of display
        summary['payment_types'] = list(filter(
            lambda tup: len(tup[1]['clients']) > 0,
            map(
                lambda x: (x, summary['payment_types_dict'][x]),
                ('cash', 'eft', 'credit', 'cheque', 'check')
            )
        ))
        pprint.pprint(summary['payment_types'], indent=4)
        context['summary'] = summary

        # Throw a warning if there's any main_dish order with size=None.
        q = Order_item.objects.filter(
            Q(order__in=billing.orders.all()) &
            (Q(size__isnull=True) | Q(size='')) &
            Q(component_group='main_dish')
        )
        if q.exists():
            size_none_orders_info = list(q.values_list(
                'order__id',
                'order__client__member__firstname',
                'order__client__member__lastname'
            ))
            formatted_htmls = ['<ul class="ui list">']
            for i, f, l in size_none_orders_info:
                formatted_htmls.append(
                    '<li><a href="{0}" target="_blank">'
                    '#{1} ({2} {3})'
                    '</a></li>'.format(
                        Order(id=i).get_absolute_url(),
                        i,
                        f,
                        l
                    )
                )
            formatted_htmls.append('</ul>')
            formatted_html = ''.join(formatted_htmls)
            messages.add_message(
                self.request, messages.WARNING,
                string_concat(
                    _('Warning: the order(s) below have not set a "size" '
                      'for main dish and thus have been excluded in '
                      '"Total Main Dishes" column.'),
                    '<br/>',
                    formatted_html
                )
            )
        return context


class BillingOrdersView(generic.DetailView):
    # Display orders detail of billing
    model = Billing
    template_name = "billing/view_orders.html"
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingOrdersView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BillingOrdersView, self).get_context_data(**kwargs)

        if self.request.GET.get('client'):
            # has ?client=client_id
            client_id = int(self.request.GET['client'])
            orders = self.object.orders.filter(client__id=client_id)
            context['orders'] = orders
            context['client'] = Client.objects.get(id=client_id)
        else:
            context['orders'] = self.object.orders.all()

        context['total_amount'] = sum(
            map(lambda o: o.price, context['orders'])
        )
        context['clients'] = list(set(map(
            lambda o: o.client,
            self.object.orders.all()
        )))
        return context


class BillingDelete(generic.DeleteView):
    model = Billing
    template_name = 'billing_confirm_delete.html'

    def get_success_url(self):
        # 'next' parameter should always be included in POST'ed URL.
        return self.request.GET['next']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingDelete, self).dispatch(*args, **kwargs)
