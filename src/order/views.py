import csv
import json
from django.http import HttpResponse, JsonResponse
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from datetime import datetime

from order.models import Order, OrderFilter, \
    ORDER_STATUS, OrderStatusChange
from order.mixins import AjaxableResponseMixin, FormValidAjaxableResponseMixin
from order.forms import CreateOrderItem, UpdateOrderItem, \
    CreateOrdersBatchForm, OrderStatusChangeForm

from meal.models import COMPONENT_GROUP_CHOICES, COMPONENT_GROUP_CHOICES_SIDES
from meal.settings import COMPONENT_SYSTEM_DEFAULT
from member.models import Client, DAYS_OF_WEEK


class OrderList(
        LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    context_object_name = 'orders'
    model = Order
    paginate_by = 20
    permission_required = 'sous_chef.read'
    template_name = 'list.html'

    def get_queryset(self):
        uf = OrderFilter(self.request.GET)
        return uf.qs.select_related(
            'client__member'
        ).prefetch_related('orders')

    def get_context_data(self, **kwargs):
        uf = OrderFilter(self.request.GET, queryset=self.get_queryset())

        context = super(OrderList, self).get_context_data(**kwargs)

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

    def get(self, request, **kwargs):

        self.format = request.GET.get('format', False)

        if self.format == 'csv':
            return ExportCSV(
                self, self.get_queryset()
            )

        return super(OrderList, self).get(request, **kwargs)


class OrderDetail(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Order
    permission_required = 'sous_chef.read'
    template_name = 'view.html'
    context_object_name = 'order'
    queryset = Order.objects.all().prefetch_related(
        'orders'
    )

    def get_context_data(self, **kwargs):
        context = super(OrderDetail, self).get_context_data(**kwargs)
        context['status'] = ORDER_STATUS
        return context


class CreateOrder(
        AjaxableResponseMixin, LoginRequiredMixin,
        PermissionRequiredMixin, CreateWithInlinesView):
    fields = ['client', 'delivery_date']
    inlines = [CreateOrderItem]
    model = Order
    permission_required = 'sous_chef.edit'
    template_name = 'create.html'

    # TODO: Change the validation of the form,
    # If component is present, then component_group is not required
    # and vice versa

    def get_success_url(self):
        return self.object.get_absolute_url()


class CreateOrdersBatch(
        LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    permission_required = 'sous_chef.edit'
    success_url = reverse_lazy('order:create_batch')
    template_name = "order/create_batch.html"

    def get_form(self, *args, **kwargs):
        k = self.get_form_kwargs()  # kwargs to initialize the form
        if self.request.method == "POST" and \
           self.request.POST.get('delivery_dates'):
            k['delivery_dates'] = self.request.POST[
                'delivery_dates'
            ].split('|')

        return CreateOrdersBatchForm(**k)

    def get_context_data(self, **kwargs):
        context = super(CreateOrdersBatch, self).get_context_data(**kwargs)
        # Define here any needed variable for template
        context["meals"] = list(filter(
            lambda tup: tup[0] != COMPONENT_GROUP_CHOICES_SIDES,
            COMPONENT_GROUP_CHOICES
        ))

        # delivery_dates
        if self.request.method == "POST" and \
           self.request.POST.get('delivery_dates'):
            delivery_dates = self.request.POST['delivery_dates'].split('|')
        else:
            delivery_dates = []

        # dates of orders to override
        if self.request.method == "POST" and \
           self.request.POST.get('override_dates'):
            override_dates = self.request.POST['override_dates'].split('|')
            override_dates = [x for x in override_dates if x in delivery_dates]
        else:
            override_dates = []

        # inactive accordion dates
        if self.request.method == "POST" and \
           self.request.POST.get('accordions_inactive'):
            context[
                'accordions_inactive'
            ] = self.request.POST['accordions_inactive'].split('|')
        else:
            context['accordions_inactive'] = []

        if self.request.method == "POST" and \
           self.request.POST.get('client'):
            c = Client.objects.get(pk=self.request.POST['client'])
            if c.delivery_type == 'E':  # episodic
                meals_default_dict = dict(c.meals_default)
            else:
                meals_default_dict = dict(c.meals_schedule)
            context['client'] = c

            # The dates where an order already exists.
            today = timezone.datetime.today()
            ordered_dates = c.orders.filter(
                delivery_date__gte=today
            ).exclude(status='C').order_by('delivery_date').values_list(
                'delivery_date', flat=True
            )
            context['ordered_dates'] = '|'.join(map(
                lambda d: d.strftime('%Y-%m-%d'),
                ordered_dates
            ))
        else:
            meals_default_dict = dict(
                map(
                    lambda x: (x[0], None),
                    DAYS_OF_WEEK
                ),
            )
        context['delivery_dates'] = []
        DAYS_OF_WEEK_DICT = dict(DAYS_OF_WEEK)

        for date in delivery_dates:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            # sunday = 0, saturday = 6
            day = ("sunday", "monday", "tuesday", "wednesday", "thursday",
                   "friday", "saturday")[int(date_obj.strftime('%w'))]

            if date not in override_dates and context.get('client'):
                order_on_day = context['client'].orders\
                    .filter(delivery_date=date_obj).exclude(status='C').first()
                if context.get('client') and order_on_day:
                    # the client has an active order already on this day.
                    # show the warning modal if it's not already being shown.
                    context['show_override_modal'] = True
                    context['order_to_override'] = order_on_day

            if not meals_default_dict[day]:  # None or {}
                # system default
                default_json = json.dumps(
                    COMPONENT_SYSTEM_DEFAULT
                )
            else:
                # client default
                default_json = json.dumps(meals_default_dict[day])

            context['delivery_dates'].append(
                (date, date_obj, default_json)
            )

        context['override_dates'] = '|'.join(override_dates)
        return context

    def form_invalid(self, form, **kwargs):
        # open accordions if there's an invalid field in it.
        context = self.get_context_data(**kwargs)
        context['form'] = form
        for field in form.errors.keys():
            try:
                # next() - find first occurence
                invalid_date = next(
                    date for date in context['accordions_inactive']
                    if date in field
                )
                context['accordions_inactive'].remove(invalid_date)
            except StopIteration:
                pass
        return self.render_to_response(context)

    def form_valid(self, form):
        # Get posted datas
        del_dates = form.cleaned_data['delivery_dates'].split('|')
        ovr_dates = form.cleaned_data['override_dates'].split('|')
        client = form.cleaned_data['client']
        items = form.cleaned_data
        del items['delivery_dates']
        del items['client']

        # Place orders using posted datas
        created_orders = Order.objects.create_batch_orders(
            del_dates, client, items, override_dates=ovr_dates,
            return_created_orders=True
        )

        # check created and uncreated dates
        created_dates = []
        for order in created_orders:
            d = order.delivery_date.strftime('%Y-%m-%d')
            created_dates.append(d)
        uncreated_dates = []
        for d in del_dates:
            if d not in created_dates:
                uncreated_dates.append(d)

        # Alert user on order placement
        if created_dates:
            messages.add_message(
                self.request, messages.SUCCESS,
                (_('%(n)s order(s) successfully placed '
                   'for %(client)s on %(dates)s.') % {
                       'n': len(created_dates),
                       'client': client,
                       'dates': ', '.join(created_dates)
                })
            )
        if uncreated_dates:
            messages.add_message(
                self.request, messages.WARNING,
                (_('%(n)s existing order(s) skipped '
                   'for %(client)s on %(dates)s.') % {
                       'n': len(uncreated_dates),
                       'client': client,
                       'dates': ', '.join(uncreated_dates)
                })
            )

        response = super(CreateOrdersBatch, self).form_valid(form)
        return response


class UpdateOrder(
        LoginRequiredMixin, PermissionRequiredMixin,
        AjaxableResponseMixin, UpdateWithInlinesView):
    fields = ['client', 'delivery_date']
    inlines = [UpdateOrderItem]
    model = Order
    permission_required = 'sous_chef.edit'
    template_name = 'update.html'

    def get_form(self, *args, **kwargs):
        form = super(UpdateOrder, self).get_form(*args, **kwargs)
        form.fields['client'].queryset = Client.objects.all().select_related(
            'member'
        ).only(
            'member__firstname',
            'member__lastname'
        )
        return form

    def get_success_url(self):
        return self.object.get_absolute_url()


class UpdateOrderStatus(
        LoginRequiredMixin, PermissionRequiredMixin,
        FormValidAjaxableResponseMixin, generic.CreateView):
    form_class = OrderStatusChangeForm
    model = OrderStatusChange
    permission_required = 'sous_chef.edit'
    template_name = "order_update_status.html"

    def get_context_data(self, **kwargs):
        context = super(UpdateOrderStatus, self).get_context_data(**kwargs)
        context['order'] = get_object_or_404(
            Order, pk=self.kwargs.get('pk')
        )
        context['order_status'] = ORDER_STATUS
        context['order_no_charge'] = 'N'
        context['order_no_charge_reasons'] = (
            _('Restrictions mistake'),
            _('Delivery mistake'),
            _('Really unhappy client')
        )
        return context

    def get_initial(self):
        order = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        return {
            'order': self.kwargs.get('pk'),
            'status_from': order.status,
            'status_to': self.request.GET.get('status'),
        }

    def form_valid(self, form):
        response = super(UpdateOrderStatus, self).form_valid(form)
        messages.add_message(
            self.request, messages.SUCCESS,
            _("The status has been changed")
        )
        return response

    def get_success_url(self):
        return reverse(
            'order:view', kwargs={'pk': self.kwargs.get('pk')}
        )


@method_decorator(csrf_exempt, name='dispatch')
class CreateDeleteOrderClientBill(
        LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'sous_chef.edit'

    def get_object(self, pk):
        return get_object_or_404(
            Order.objects.prefetch_related('orders'),
            pk=pk
        )

    def post(self, request, pk, *args, **kwargs):
        order = self.get_object(pk)
        order.includes_a_bill = True
        return HttpResponse('OK', status=200)

    def delete(self, request, pk, *args, **kwargs):
        order = self.get_object(pk)
        order.includes_a_bill = False
        return HttpResponse('OK', status=200)


class DeleteOrder(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Order
    permission_required = 'sous_chef.edit'
    template_name = 'order_confirm_delete.html'

    def get_success_url(self):
        # 'next' parameter should always be included in POST'ed URL.
        return self.request.GET.get('next') or self.request.POST['next']


def ExportCSV(request, queryset):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] =\
        'attachment; filename=order_export.csv'
    writer = csv.writer(response, csv.excel)

    writer.writerow([
        "ID",
        "Client Firstname",
        "Client Lastname",
        "Order Status",
        "Creation Date",
        "Delivery Date",
        "price",
    ])

    for obj in queryset:
        writer.writerow([
            obj.id,
            obj.client.member.firstname,
            obj.client.member.lastname,
            obj.get_status_display(),
            obj.creation_date,
            obj.delivery_date,
            obj.price,
        ])

    return response
