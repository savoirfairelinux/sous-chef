import csv
from django.http import HttpResponse
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from extra_views import CreateWithInlinesView

from order.models import Order, Order_item, OrderFilter, ORDER_STATUS
from order.mixins import AjaxableResponseMixin
from order.forms import CreateOrderItem


class OrderList(generic.ListView):
    model = Order
    template_name = 'list.html'
    context_object_name = 'order'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        uf = OrderFilter(self.request.GET)
        return uf.qs

    def get_context_data(self, **kwargs):
        uf = OrderFilter(self.request.GET, queryset=self.get_queryset())

        context = super(OrderList, self).get_context_data(**kwargs)

        context['myVariableOfContext'] = 0
        context['filter'] = uf

        text = ''
        count = 0
        for getVariable in self.request.GET:
            for getValue in self.request.GET.getlist(getVariable):
                if count == 0:
                    text += "?" + getVariable + "=" + getValue
                else:
                    text += "&" + getVariable + "=" + getValue
                count += 1

        context['get'] = text

        return context

    def get(self, request, **kwargs):

        self.format = request.GET.get('format', False)

        if self.format == 'csv':
            return ExportCSV(
                self, self.get_queryset()
                )

        return super(OrderList, self).get(request, **kwargs)


class OrderDetail(generic.DetailView):
    model = Order
    template_name = 'view.html'
    context_object_name = 'order'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrderDetail, self).get_context_data(**kwargs)
        context['status'] = ORDER_STATUS
        return context


class CreateOrder(AjaxableResponseMixin, CreateWithInlinesView):
    model = Order
    fields = '__all__'
    inlines = [CreateOrderItem]
    template_name = 'create.html'

    # TODO: Change the validation of the form,
    # If component is present, then component_group is not required
    # and vice versa

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CreateOrder, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return self.object.get_absolute_url()


class UpdateOrder(AjaxableResponseMixin, generic.UpdateView):
    model = Order
    fields = '__all__'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateOrder, self).dispatch(*args, **kwargs)


class UpdateOrderStatus(UpdateOrder):
    fields = ['status']


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
