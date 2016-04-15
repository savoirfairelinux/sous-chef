# coding: utf-8

from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class ClientList(generic.ListView):
    # Display the list of clients
    template_name = 'client/list.html'
    context_object_name = 'client'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # Here you need to return the list of clients
        return 0

    def get_context_data(self, **kwargs):
        context = super(ClientList, self).get_context_data(**kwargs)

        # Here you add some variable of context to display on template
        context['myVariableOfContext'] = 0

        return context
