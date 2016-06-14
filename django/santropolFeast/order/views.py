from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from member.models import Client


def show_order_information(request, id):
    client = get_object_or_404(Client, pk=id)

    return render(request, 'list_order.html',
                  {'client': client}
                  )
