from django.shortcuts import render
from django.views import generic
from billing.models import (
    Billing, OrderBilling, calculate_amount_total, BillingFilter
    )
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from order.models import Order
from django.http import HttpResponseRedirect


class BillingList(generic.ListView):
    # Display the billing list
    model = Billing
    template_name = "list_billing.html"
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        uf = BillingFilter(self.request.GET, queryset=self.get_queryset)
        return uf.qs

    def get_context_data(self, **kwargs):
        uf = BillingFilter(self.request.GET, queryset=self.get_queryset())
        context = super(BillingList, self).get_context_data(**kwargs)

        # Context variable
        context['myVariableOfContext'] = 0
        context['filter'] = uf

        return context


class BillingCreate(generic.CreateView):
    # View to create the billing

    model = Billing
    template_name = "create.html"
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingCreate, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO get 3 variable: year, month ,and client

        context = super(BillingCreate, self).get_context_data(**kwargs)

        # Context variable
        context['myVariableOfContext'] = 0

        return context

    def create_bill(client, year, month):

        orders = Order.objects.get_orders_for_month_client(month, year, client)

        billing = Billing.objects.create(
            client=client,
            total_amount=calculate_amount_total(orders),
            billing_month=month,
            billing_year=year,
            generation_date=datetime.now(),
            detail=get_order_detail(orders),
        )

        for order in orders:
            OrderBilling.objects.create(
                order_id=order.id,
                billing_id=billing.id
            )

        return HttpResponseRedirect(reverse_lazy('billing:list'))


class BillingView(generic.DetailView):
    # Display detail of billing
    model = Billing
    template_name = "view.html"
    context_object_name = "billing"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BillingView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BillingView, self).get_context_data(**kwargs)

        # Context variable
        context['myVariableOfContext'] = 0

        return context


class BillingDelete(generic.DeleteView):
    pass
