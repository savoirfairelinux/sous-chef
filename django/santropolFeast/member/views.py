# coding: utf-8

from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from member.models import Client, Member


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


class ClientView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/detail.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientView, self).get_context_data(**kwargs)

        # Here you add some variable of context to display on template
        context['myVariableOfContext'] = 0

        return context


class MemberUpdate(generic.UpdateView):
    # Display the form to update a member
    model = Member
    template_name = "member/update.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Here you need to check if the client exist
        # You can use for example get_object_or_404()
        # note: self.kwargs["pk"] is the ID of the client given by the urls.py

        return super(MemberUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        # Here you redirect to the next page
        # You can use for example reverse_lazy()

        return 0
