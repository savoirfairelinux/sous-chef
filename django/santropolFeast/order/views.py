from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.views import generic
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from member.models import Client
from order.models import Order, OrderFilter
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import csv


class OrderList(generic.ListView):
    # Display the list of clients
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


def ExportCSV(request, queryset):
    reponse = HttpResponse(content_type="text/csv")
    reponse['Content-Disposition'] =\
        'attachment; filename=order_export.csv'
    writer = csv.writer(reponse, csv.excel)

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

    return reponse


def show_information(request, id):
    order = get_object_or_404(Order, pk=id)
    return render(request, 'view.html', {'order': order})
