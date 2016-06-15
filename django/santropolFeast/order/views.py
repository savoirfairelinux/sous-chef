from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from member.models import Client
from order.models import Order
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


def show_order_information(request, id):
    client = get_object_or_404(Client, pk=id)

    return render(request, 'list_order.html',
                  {'client': client}
                  )


class OrderList(generic.ListView):
    # Display the list of clients
    model = Order
    template_name = 'list_all_order.html'
    context_object_name = 'order'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderList, self).dispatch(*args, **kwargs)
