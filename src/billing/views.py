import copy
import collections

from django.db.models import Q, Count, Prefetch
from django.views import generic
from django.utils.translation import string_concat
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages

from billing.models import (
    Billing, BillingFilter
)
from order.models import DeliveredOrdersByMonth
from django.core.urlresolvers import reverse_lazy
from order.models import Order, Order_item
from django.http import HttpResponseRedirect
from member.models import Client


class BillingList(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    # Display the billing list
    context_object_name = "billings"
    model = Billing
    permission_required = 'sous_chef.read'
    template_name = "billing/list.html"

    def get_context_data(self, **kwargs):
        context = super(BillingList, self).get_context_data(**kwargs)
        uf = BillingFilter(self.request.GET, queryset=self.get_queryset())
        context['filter'] = uf

        return context

    def get_queryset(self):
        uf = BillingFilter(self.request.GET)
        return uf.qs.annotate(Count('orders', distinct=True))


class BillingCreate(LoginRequiredMixin, PermissionRequiredMixin, generic.CreateView):
    # View to create the billing
    context_object_name = "billing"
    model = Billing
    permission_required = 'sous_chef.edit'

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


class BillingAdd(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    context_object_name = "orders"
    model = Order
    paginate_by = 20
    permission_required = 'sous_chef.edit'
    template_name = "billing/add.html"

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
        return uf.qs.select_related(
            'client__member'
        ).only(
            'status',
            'delivery_date',
            'client__member__firstname',
            'client__member__lastname'
        ).prefetch_related(Prefetch(
            'orders',
            queryset=Order_item.objects.all().only(
                'order__id',
                'price',
                'billable_flag'
            )
        ))


class BillingSummaryView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    # Display summary of billing
    model = Billing
    permission_required = 'sous_chef.read'
    template_name = "billing/view.html"
    context_object_name = "billing"
    queryset = Billing.objects.prefetch_related(Prefetch(
        'orders',
        queryset=Order.objects.all().select_related(
            'client__member'
        ).only(
            'client__member__firstname',
            'client__member__lastname',
            'client__rate_type',
            'client__billing_payment_type'
        ).prefetch_related(Prefetch(
            'orders',
            queryset=Order_item.objects.all().only(
                'order__id',
                'price',
                'billable_flag',
                'size',
                'component_group',
                'total_quantity'
            )
        ))
    ))

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
                'payment_type': client.get_billing_payment_type_display() if (
                    client.billing_payment_type is not None) else '',
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

        # sort clients in each payment type group
        for payment_type, statistics in summary['payment_types_dict'].items():
            statistics['clients'].sort(
                key=lambda c: (c['lastname'], c['firstname'])
            )

        # reorder the display for supported & non-supported payment types
        summary['payment_types'] = sorted(
            summary['payment_types_dict'].items(),
            key=lambda tup: {
                ' ': 0,      # 0th position
                'credit': 1,    # 1st position
                'eft': 2,     # 2nd position
                '3rd': 3,  # 3rd position
            }.get(tup[0], 99)  # last position(s)
        )

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


class BillingOrdersView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    # Display orders detail of billing
    model = Billing
    permission_required = 'sous_chef.read'
    template_name = "billing/view_orders.html"
    context_object_name = "billing"

    queryset = Billing.objects.prefetch_related(Prefetch(
        'orders',
        queryset=Order.objects.all().select_related(
            'client__member'
        ).only(
            'status',
            'delivery_date',
            'client__member__firstname',
            'client__member__lastname'
        ).prefetch_related(Prefetch(
            'orders',
            queryset=Order_item.objects.all().only(
                'order__id',
                'price',
                'billable_flag'
            )
        ))
    ))

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


class BillingDelete(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Billing
    permission_required = 'sous_chef.edit'
    template_name = 'billing_confirm_delete.html'

    def get_success_url(self):
        # 'next' parameter should always be included in POST'ed URL.
        return self.request.GET.get('next') or self.request.POST['next']
