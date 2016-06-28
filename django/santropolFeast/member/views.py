# coding: utf-8

from django.views import generic
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from member.models import Client, Member, Address, Contact, Note
from member.models import Referencing, ClientFilter, Note, ClientFilter
from formtools.wizard.views import NamedUrlSessionWizardView
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy


class ClientWizard(NamedUrlSessionWizardView):

    template_name = 'forms/form.html'

    def done(self, form_list, form_dict, **kwargs):

        self.form_dict = form_dict
        self.save()
        return HttpResponseRedirect(reverse_lazy('member:list'))

    def save(self):
        """Save the client"""

        basic_information = self.form_dict['basic_information']
        address_information = self.form_dict['address_information']
        referent_information = self.form_dict['referent_information']
        payment_information = self.form_dict['payment_information']
        dietary_restriction = self.form_dict['dietary_restriction']
        emergency_contact = self.form_dict['emergency_contact']

        address = Address.objects.create(
            number=address_information.cleaned_data.get('number'),
            street=address_information.cleaned_data.get('street'),
            apartment=address_information.cleaned_data.get(
                'apartment'
            ),
            floor=address_information.cleaned_data.get('floor'),
            city=address_information.cleaned_data.get('city'),
            postal_code=address_information.cleaned_data.get('postal_code'),
        )
        address.save()

        member = Member.objects.create(
            firstname=basic_information.cleaned_data.get('firstname'),
            lastname=basic_information.cleaned_data.get('lastname'),
            address=address,
        )
        member.save()

        # Should be created only if third-party billing member
        if True:
            billing_address = Address.objects.create(
                number=payment_information.cleaned_data.get('number'),
                street=payment_information.cleaned_data.get('street'),
                apartment=payment_information.cleaned_data.get('apartment'),
                floor=payment_information.cleaned_data.get('floor'),
                city=payment_information.cleaned_data.get('city'),
                postal_code=payment_information.cleaned_data.get(
                    'postal_code'
                ),
            )
            billing_address.save()

            billing_member = Member.objects.create(
                firstname=payment_information.cleaned_data.get('firstname'),
                lastname=payment_information.cleaned_data.get('lastname'),
                address=address,
            )
            billing_member.save()
        else:
            billing_member = member

        contact = Contact.objects.create(
            type=basic_information.cleaned_data.get('contact_type'),
            value=basic_information.cleaned_data.get("contact_value"),
            member=member,
        )
        contact.save()

        emergency = Member.objects.create(
            firstname=emergency_contact.cleaned_data.get("firstname"),
            lastname=emergency_contact.cleaned_data.get('lastname'),
        )
        emergency.save()

        client_emergency_contact = Contact.objects.create(
            type=emergency_contact.cleaned_data.get("contact_type"),
            value=emergency_contact.cleaned_data.get(
                "contact_value"
            ),

            member=emergency,
        )
        client_emergency_contact.save()

        client = Client.objects.create(
            rate_type=payment_information.cleaned_data.get("facturation"),
            billing_payment_type=payment_information.cleaned_data.get(
                "billing_payment_type"),
            member=member,
            billing_member=billing_member,
            emergency_contact=emergency,
            language=basic_information.cleaned_data.get('language'),
            gender=basic_information.cleaned_data.get('gender'),
            birthdate=basic_information.cleaned_data.get('birthdate'),
            alert=basic_information.cleaned_data.get("alert"),
            delivery_type=dietary_restriction.cleaned_data.get(
                "delivery_type"
                ),
            meal_default_monday={'size_monday':
                                 dietary_restriction.cleaned_data.get(
                                    'size_monday'
                                  ),
                                 'main_dish_monday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'main_dish_monday_quantity'
                                    ), 'dessert_monday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'dessert_monday_quantity'
                                    ), 'diabetic_monday_quantity':
                                        dietary_restriction.cleaned_data.get(
                                    'diabetic_monday_quantity'
                                    ), 'fruit_salad_monday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'fruit_salad_monday_quantity'
                                    ), 'green_salad_monday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'green_salad_monday_quantity'
                                    ), 'pudding_monday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'pudding_monday_quantity'
                                    ), 'compote_monday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'compote_monday_quantity'
                                    ),
                                 },

            meal_default_tuesday={'size_tuesday':
                                  dietary_restriction.cleaned_data.get(
                                    'size_tuesday'
                                  ), 'main_dish_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'main_dish_tuesday_quantity'
                                  ), 'dessert_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'dessert_tuesday_quantity'
                                  ), 'diabetic_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'diabetic_tuesday_quantity'
                                  ), 'fruit_salad_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'fruit_salad_tuesday_quantity'
                                  ), 'green_salad_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'green_salad_tuesday_quantity'
                                  ), 'pudding_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'pudding_tuesday_quantity'
                                  ), 'compote_tuesday_quantity':
                                  dietary_restriction.cleaned_data.get(
                                    'compote_tuesday_quantity'
                                  )
                                  },

            meal_default_wednesday={'size_wednesday':
                                    dietary_restriction.cleaned_data.get(
                                        'size_wednesday'
                                    ), 'main_dish_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'main_dish_wednesday_quantity'
                                    ), 'dessert_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'dessert_wednesday_quantity'
                                    ), 'diabetic_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'diabetic_wednesday_quantity'
                                    ), 'fruit_salad_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'fruit_salad_wednesday_quantity'
                                    ), 'green_salad_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'green_salad_wednesday_quantity'
                                    ), 'pudding_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'pudding_wednesday_quantity'
                                    ), 'compote_wednesday_quantity':
                                    dietary_restriction.cleaned_data.get(
                                        'compote_wednesday_quantity'
                                    )

                                    },

            meal_default_thursday={'size_thursday':
                                   dietary_restriction.cleaned_data.get(
                                    'size_thursday'
                                   ), 'main_dish_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'main_dish_thursday_quantity'
                                   ), 'dessert_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'dessert_thursday_quantity'
                                   ), 'diabetic_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'diabetic_thursday_quantity'
                                   ), 'fruit_salad_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'fruit_salad_thursday_quantity'
                                   ), 'green_salad_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'green_salad_thursday_quantity'
                                   ), 'pudding_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'pudding_thursday_quantity'
                                   ), 'compote_thursday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'compote_thursday_quantity'
                                   )
                                   },

            meal_default_friday={'size_friday':
                                 dietary_restriction.cleaned_data.get(
                                    'size_friday'
                                   ), 'main_dish_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'main_dish_friday_quantity'
                                   ), 'dessert_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'dessert_friday_quantity'
                                   ), 'diabetic_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'diabetic_friday_quantity'
                                   ), 'fruit_salad_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'fruit_salad_friday_quantity'
                                   ), 'green_salad_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'green_salad_friday_quantity'
                                   ), 'pudding_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'pudding_friday_quantity'
                                   ), 'compote_friday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'compote_friday_quantity'
                                   )
                                 },

            meal_default_saturday={'size_saturday':
                                   dietary_restriction.cleaned_data.get(
                                    'size_saturday'
                                   ), 'main_dish_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'main_dish_saturday_quantity'
                                   ), 'dessert_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'dessert_saturday_quantity'
                                   ), 'diabetic_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'diabetic_saturday_quantity'
                                   ), 'fruit_salad_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'fruit_salad_saturday_quantity'
                                   ), 'green_salad_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'green_salad_saturday_quantity'
                                   ), 'pudding_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'pudding_saturday_quantity'
                                   ), 'compote_saturday_quantity':
                                   dietary_restriction.cleaned_data.get(
                                    'compote_saturday_quantity'
                                   )
                                   },

            meal_default_sunday={'size_sunday':
                                 dietary_restriction.cleaned_data.get(
                                    'size_sunday'
                                   ), 'main_dish_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'main_dish_sunday_quantity'
                                   ), 'dessert_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'dessert_sunday_quantity'
                                   ), 'diabetic_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'diabetic_sunday_quantity'
                                   ), 'fruit_salad_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'fruit_salad_sunday_quantity'
                                   ), 'green_salad_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'green_salad_sunday_quantity'
                                   ), 'pudding_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'pudding_sunday_quantity'
                                   ), 'compote_sunday_quantity':
                                 dietary_restriction.cleaned_data.get(
                                    'compote_sunday_quantity'
                                   )
                                 }
        )

        if dietary_restriction.cleaned_data.get('status'):
            client.status = 'A'

        client.save()

        referent = Member.objects.create(
            firstname=referent_information.cleaned_data.get(
                "firstname"
            ),
            lastname=referent_information.cleaned_data.get(
                "lastname"
            ),
        )
        referent.save()

        referencing = Referencing.objects.create(
            referent=referent,
            client=client,
            referral_reason=referent_information.cleaned_data.get(
                "referral_reason"
            ),
            work_information=referent_information.cleaned_data.get(
                'work_information'
            ),
            date=referent_information.cleaned_data.get(
                'date'
            ),
        )
        referencing.save()


class ClientList(generic.ListView):
    # Display the list of clients
    model = Client
    template_name = 'client/list.html'
    context_object_name = 'clients'
    paginate_by = 21

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        uf = ClientFilter(self.request.GET)
        return uf.qs

    def get_context_data(self, **kwargs):
        uf = ClientFilter(self.request.GET, queryset=self.get_queryset())

        context = super(ClientList, self).get_context_data(**kwargs)

        # Here you add some variable of context to display on template
        context['myVariableOfContext'] = 0
        context['filter'] = uf
        context['display'] = self.request.GET.get('display', 'block')
        text = ''
        count = 0
        for getVariable in self.request.GET:
            if getVariable == "display" or getVariable == "page":
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


class ClientInfoView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/information.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientInfoView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientInfoView, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class ClientReferentView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/referent.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientReferentView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientReferentView, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class ClientAddressView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/address.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientAddressView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientAddressView, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class ClientPaymentView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/payment.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientPaymentView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientPaymentView, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class ClientAllergiesView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/allergies.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientAllergiesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientAllergiesView, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


def show_information(request, id):
    client = get_object_or_404(Client, pk=id)
    notes = list(Note.objects.all())

    return render(request, 'client/view/view.html',
                  {'client': client, 'notes': notes})


class ClientPreferencesView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/preferences.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientPreferencesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientPreferencesView, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class MemberUpdate(generic.UpdateView):
    # Display the form to update a member
    model = Member
    template_name = "client/update.html"

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

    def get_context_data(self, **kwargs):
        context = super(MemberUpdate, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class ClientAllergiesUpdate(generic.UpdateView):
    # Display the form to update allergies of a client
    model = Client
    template_name = "client/update.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Here you need to check if the client exist
        # You can use for example get_object_or_404()
        # note: self.kwargs["pk"] is the ID of the client given by the urls.py

        return super(ClientAllergiesUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        # Here you redirect to the next page
        # You can use for example reverse_lazy()

        return 0

    def get_context_data(self, **kwargs):
        context = super(ClientAllergiesUpdate, self).get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class ClientPreferencesUpdate(generic.UpdateView):
    # Display the form to update preference of a client
    model = Client
    template_name = "client/update.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # Here you need to check if the client exist
        # You can use for example get_object_or_404()
        # note: self.kwargs["pk"] is the ID of the client given by the urls.py

        return super(ClientPreferencesUpdate, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        # Here you redirect to the next page
        # You can use for example reverse_lazy()

        return 0

    def get_context_data(self, **kwargs):
        context = super(ClientPreferencesUpdate, self).\
            get_context_data(**kwargs)

        """
        Here we need to add some variable of context to send to template :
         1 - A string active_tab who can be:
            'info'
            'referent'
            'address'
            'payment'
            'allergies'
            'preferences'
        """
        context['myVariableOfContext'] = 0

        return context


class NoteList(generic.ListView):
    # Display the list of clients
    model = Note
    template_name = 'notes/list.html'
    context_object_name = 'notes'


def mark_as_read(request, id):
    note = get_object_or_404(Note, pk=id)
    note.mark_as_read()
    return HttpResponseRedirect(reverse_lazy("member:notes"))
