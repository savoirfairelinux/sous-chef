from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from member.models import Client
from order.models import Order, OrderFilter
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


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


def show_information(request, id):
    order = get_object_or_404(Order, pk=id)

    return render(request, 'view_order.html', {'order': order})
