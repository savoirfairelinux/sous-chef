from django.shortcuts import render
from django.views import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from billing.models import (
    Billing, calculate_amount_total, BillingFilter
)
from order.models import DeliveredOrdersByMonth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from order.models import Order
from django.http import HttpResponseRedirect


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


class BillingView(generic.DetailView):
    # Display detail of billing
    model = Billing
    template_name = "billing/view.html"
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BillingView, self).get_context_data(**kwargs)
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
