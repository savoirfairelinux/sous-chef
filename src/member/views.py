# coding: utf-8


import csv
from datetime import date
import json
from django.core.urlresolvers import reverse_lazy
from django.views import generic
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from member.forms import load_initial_data
from member.models import (
    Client,
    ClientScheduledStatus,
    Member,
    Address,
    Contact,
    Referencing,
    Restriction,
    Client_option,
    ClientFilter,
    ClientScheduledStatusFilter,
    DAYS_OF_WEEK,
    Route,
    Client_avoid_ingredient,
    Client_avoid_component,
)
from member.forms import (
    ClientScheduledStatusForm,
    ClientBasicInformation,
    ClientAddressInformation,
    ClientReferentInformation,
)
from note.models import Note
from order.mixins import AjaxableResponseMixin
from meal.models import COMPONENT_GROUP_CHOICES
from formtools.wizard.views import NamedUrlSessionWizardView


class ClientUpdateBasicInformation(generic.edit.FormView):
    template_name = 'client/update/basic_information.html'
    form_class = ClientBasicInformation
    success_url = reverse_lazy('member:list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(
            ClientUpdateBasicInformation,
            self).dispatch(
            *args,
            **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateBasicInformation,
            self).get_context_data(
            **kwargs)
        context.update({
            'client_id': self.kwargs['client_id'],
            'current_step': 'basic_information'
        })
        return context

    def get_initial(self):
        initial = super(ClientUpdateBasicInformation, self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('client_id')
        )
        initial = load_initial_data(client)
        return initial

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        client = get_object_or_404(
            Client, pk=self.kwargs.get('client_id')
        )
        self.save(form.cleaned_data, client)
        return super(ClientUpdateBasicInformation, self).form_valid(form)

    def save(self, form, client):
        """
        Save the basic information step data.
        """
        client.member.firstname = form['firstname']
        client.member.lastname = form['lastname']
        client.member.save()

        client.gender = form['gender']
        client.birthdate = form['birthdate']
        client.language = form['language']
        client.alert = form['alert']
        client.save()


class ClientUpdateAddressInformation(generic.edit.FormView):
    template_name = 'client/update/address_information.html'
    form_class = ClientAddressInformation
    success_url = reverse_lazy('member:list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(
            ClientUpdateAddressInformation,
            self).dispatch(
            *args,
            **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateAddressInformation,
            self).get_context_data(
            **kwargs)
        context.update({'current_step': 'address_information'})
        context.update({'client_id': self.kwargs['client_id']})
        return context

    def get_initial(self):
        initial = super(ClientUpdateAddressInformation, self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('client_id')
        )
        initial = load_initial_data(client)
        return initial

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        client = get_object_or_404(
            Client, pk=self.kwargs.get('client_id')
        )
        self.save(form.cleaned_data, client)
        return super(ClientUpdateAddressInformation, self).form_valid(form)

    def save(self, form, client):
        """
        Save the basic information step data.
        """
        client.member.address.street = form['street']
        client.member.address.apartment = form['apartment']
        client.member.address.city = form['city']
        client.member.address.postal_code = form['postal_code']
        client.member.address.distance = form['distance']
        client.member.address.latitude = form['latitude']
        client.member.address.longitude = form['longitude']
        client.member.address.save()

        client.route = form['route']
        client.delivery_note = form['delivery_note']
        client.save()


class ClientUpdateReferentInformation(generic.edit.FormView):
    template_name = 'client/update/referent_information.html'
    form_class = ClientReferentInformation
    success_url = reverse_lazy('member:list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(
            ClientUpdateReferentInformation,
            self).dispatch(
            *args,
            **kwargs)

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateReferentInformation,
            self).get_context_data(
            **kwargs)
        context.update({'current_step': 'referent_information'})
        context.update({'client_id': self.kwargs['client_id']})
        return context

    def get_initial(self):
        initial = super(ClientUpdateReferentInformation, self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('client_id')
        )
        initial = load_initial_data(client)
        return initial

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        client = get_object_or_404(
            Client, pk=self.kwargs.get('client_id')
        )
        self.save(form.cleaned_data, client)
        return super(ClientUpdateReferentInformation, self).form_valid(form)

    def save(self, form, client):
        """
        Save the basic information step data.
        """
        client.member.address.street = form['street']
        client.member.address.apartment = form['apartment']
        client.member.address.city = form['city']
        client.member.address.postal_code = form['postal_code']
        client.member.address.distance = form['distance']
        client.member.address.latitude = form['latitude']
        client.member.address.longitude = form['longitude']
        client.member.address.save()

        client.route = form['route']
        client.delivery_note = form['delivery_note']
        client.save()


class ClientWizard(NamedUrlSessionWizardView):

    template_name = 'client/create/form.html'

    def get_context_data(self, **kwargs):
        context = super(ClientWizard, self).get_context_data(**kwargs)

        context["weekday"] = DAYS_OF_WEEK
        context["meals"] = COMPONENT_GROUP_CHOICES

        if 'client_id' in kwargs:
            context.update({'edit': True})
            context.update({'client_id': kwargs['client_id']})

        return context

    def get_form_initial(self, step):
        """
        Load initial data.
        """
        initial = {}
        if 'client_id' in self.kwargs:
            client_id = self.kwargs['client_id']
            client = Client.objects.get(id=client_id)
            initial = self.load_initial_data(step, client)

        return self.initial_dict.get(step, initial)

    def done(self, form_list, form_dict, **kwargs):
        """
        Process the submitted and validated form data.
        """
        # Use form_dict which allows us to access the wizard’s forms
        # based on their step names.
        client_id = None
        self.form_dict = form_dict

        if 'client_id' in kwargs:
            client_id = kwargs['client_id']
        self.save(client_id)
        return HttpResponseRedirect(reverse_lazy('member:list'))

    def load_initial_data(self, step, client):
        """
        Load initial for the given step and client.
        """
        initial = {
            'firstname': client.member.firstname,
            'lastname': client.member.lastname,
            'alert': client.alert,
            'gender': client.gender,
            'language': client.language,
            'birthdate': client.birthdate,
            'contact_value': client.member.home_phone,
            'street': client.member.address.street,
            'city': client.member.address.city,
            'apartment': client.member.address.apartment,
            'postal_code': client.member.address.postal_code,
            'delivery_note': client.delivery_note,
            'route': client.route,
            'latitude': client.member.address.latitude,
            'longitude': client.member.address.longitude,
            'distance': client.member.address.distance,
            'work_information': client.client_referent.get().work_information,
            'referral_reason': client.client_referent.get().referral_reason,
            'date': client.client_referent.get().date,
            'member': client.id,
            'same_as_client': True,
            'facturation': '',
            'billing_payment_type': '',



        }
        return initial

    def save_json(self, dictonary):
        json = {}

        for days, Days in DAYS_OF_WEEK:
            json['size_{}'.format(days)] = dictonary.get(
                'size_{}'.format(days)
            )

            if json['size_{}'.format(days)] is "":
                json['size_{}'.format(days)] = None

            for meal, Meals in COMPONENT_GROUP_CHOICES:
                json['{}_{}_quantity'.format(meal, days)] \
                    = dictonary.get(
                    '{}_{}_quantity'.format(meal, days)
                )

        return json

    def save(self, id=None):
        """
        Update or create the member and all its related data.
        """
        basic_information = self.form_dict['basic_information'].cleaned_data
        address_information = self.form_dict[
            'address_information'].cleaned_data
        referent_information = self.form_dict[
            'referent_information'].cleaned_data
        payment_information = self.form_dict[
            'payment_information'].cleaned_data
        dietary_restriction = self.form_dict[
            'dietary_restriction'].cleaned_data

        member, created = Member.objects.update_or_create(
            id=id,
            defaults={
                'firstname': basic_information.get('firstname'),
                'lastname': basic_information.get('lastname'),
            }
        )

        address, created = Address.objects.update_or_create(
            id=None if member.address is None else member.address.id,
            defaults={
                'street': address_information.get('street'),
                'apartment': address_information.get('apartment'),
                'city': address_information.get('city'),
                'postal_code': address_information.get('postal_code'),
                'latitude': address_information.get('latitude'),
                'longitude': address_information.get('longitude'),
                'distance': address_information.get('distance'),
            }
        )
        member.address = address
        member.save()

        contact, created = Contact.objects.update_or_create(
            member=member, type=basic_information.get('contact_type'),
            defaults={
                'type': basic_information.get('contact_type'),
                'value': basic_information.get('contact_value'),
                'member': member
            }
        )

        billing_member = self.save_billing_member(member)
        emergency = self.save_emergency_contact(billing_member)

        client, created = Client.objects.update_or_create(
            id=member.id,
            defaults={
                'member': member,
                'language': basic_information.get('language'),
                'gender': basic_information.get('gender'),
                'birthdate': basic_information.get('birthdate'),
                'alert': basic_information.get('alert'),
                'rate_type': payment_information.get('facturation'),
                'billing_payment_type':
                    payment_information.get('billing_payment_type'),
                'billing_member': billing_member,
                'emergency_contact': emergency,
                'delivery_type': dietary_restriction.get('delivery_type'),
                'meal_default_week': self.save_json(dietary_restriction),
                'route': address_information.get('route'),
                'delivery_note': address_information.get('delivery_note'),
            }
        )

        self.save_referent_information(client, billing_member, emergency)
        self.save_preferences(client)

    def save_billing_member(self, member):
        payment_information = \
            self.form_dict['payment_information'].cleaned_data

        if payment_information.get('same_as_client'):
            billing_member = member

        else:
            e_b_member = payment_information.get('member')
            if self.billing_member_is_member():
                billing_member = member
            elif e_b_member:
                e_b_member_id = e_b_member.split(' ')[0].\
                    replace('[', '').replace(']', '')
                billing_member = Member.objects.get(pk=e_b_member_id)
            else:
                billing_address = Address.objects.create(
                    number=payment_information.get('number'),
                    street=payment_information.get('street'),
                    apartment=payment_information.get('apartment'),
                    floor=payment_information.get('floor'),
                    city=payment_information.get('city'),
                    postal_code=payment_information.get('postal_code'),
                )
                billing_address.save()

                billing_member = Member.objects.create(
                    firstname=payment_information.get('firstname'),
                    lastname=payment_information.get('lastname'),
                    address=billing_address,
                )
                billing_member.save()

        return billing_member

    def save_emergency_contact(self, billing_member):
        emergency_contact = self.form_dict['emergency_contact']
        e_emergency_member = emergency_contact.cleaned_data.get('member')
        if self.billing_member_is_emergency_contact(billing_member):
            emergency = billing_member
        elif e_emergency_member:
            e_emergency_member_id = e_emergency_member.split(' ')[0]\
                .replace('[', '')\
                .replace(']', '')
            emergency = Member.objects.get(pk=e_emergency_member_id)
        else:
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
        return emergency

    def save_referent_information(self, client, billing_member, emergency):
        referent_information = self.form_dict['referent_information']
        e_referent = referent_information.cleaned_data.get('member')
        if self.referent_is_billing_member():
            referent = billing_member
        elif self.referent_is_emergency_contact():
            referent = emergency
        elif e_referent:
            e_referent_id = e_referent.split(' ')[0]\
                .replace('[', '')\
                .replace(']', '')
            referent = Member.objects.get(pk=e_referent_id)
        else:
            referent = Member.objects.create(
                firstname=referent_information.cleaned_data.get("firstname"),
                lastname=referent_information.cleaned_data.get("lastname"),
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
        return referencing

    def save_preferences(self, client):
        preferences = self.form_dict['dietary_restriction'].cleaned_data

        # Save meals schedule as a Client option
        client.set_meals_schedule(
            preferences.get('meals_schedule')
        )

        # Save restricted items
        for restricted_item in preferences.get('restrictions'):
            Restriction.objects.create(
                client=client,
                restricted_item=restricted_item
            )

        # Save food preparation
        for food_preparation in preferences.get('food_preparation'):
            Client_option.objects.create(
                client=client,
                option=food_preparation
            )

        # Save ingredients to avoid
        for ingredient_to_avoid in preferences.get('ingredient_to_avoid'):
            Client_avoid_ingredient.objects.create(
                client=client,
                ingredient=ingredient_to_avoid
            )

        # Save components to avoid
        for component_to_avoid in preferences.get('dish_to_avoid'):
            Client_avoid_component.objects.create(
                client=client,
                component=component_to_avoid
            )

    def billing_member_is_member(self):
        basic_information = self.form_dict['basic_information']
        payment_information = self.form_dict['payment_information']

        b_firstname = basic_information.cleaned_data.get('firstname')
        b_lastname = basic_information.cleaned_data.get('lastname')

        p_firstname = payment_information.cleaned_data.get('firstname')
        p_lastname = payment_information.cleaned_data.get('lastname')

        if b_firstname == p_firstname and b_lastname == p_lastname:
            return True
        return False

    def billing_member_is_emergency_contact(self, billing_member):
        emergency_contact = self.form_dict['emergency_contact']

        e_firstname = emergency_contact.cleaned_data.get('firstname')
        e_lastname = emergency_contact.cleaned_data.get('lastname')

        if e_firstname == billing_member.firstname \
                and e_lastname == billing_member.lastname:
            return True

        return False

    def referent_is_emergency_contact(self):
        emergency_contact = self.form_dict['emergency_contact']
        referent_information = self.form_dict['referent_information']

        e_firstname = emergency_contact.cleaned_data.get('firstname')
        e_lastname = emergency_contact.cleaned_data.get('lastname')

        r_firstname = referent_information.cleaned_data.get("firstname")
        r_lastname = referent_information.cleaned_data.get("lastname")

        if e_firstname == r_firstname and e_lastname == r_lastname:
            return True
        return False

    def referent_is_billing_member(self):
        referent_information = self.form_dict['referent_information']
        payment_information = self.form_dict['payment_information']

        r_firstname = referent_information.cleaned_data.get("firstname")
        r_lastname = referent_information.cleaned_data.get("lastname")

        p_firstname = payment_information.cleaned_data.get('firstname')
        p_lastname = payment_information.cleaned_data.get('lastname')

        if r_firstname == p_firstname and r_lastname == p_lastname:
            return True
        return False


class ClientList(generic.ListView):
    # Display the list of clients
    model = Client
    template_name = 'client/list.html'
    context_object_name = 'clients'
    paginate_by = 20

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        uf = ClientFilter(self.request.GET)
        return uf.qs

        # The queryset must be client

    def get_context_data(self, **kwargs):
        uf = ClientFilter(self.request.GET, queryset=self.get_queryset())

        context = super(ClientList, self).get_context_data(**kwargs)

        # Here you add some variable of context to display on template
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

    def get(self, request, **kwargs):

        self.format = request.GET.get('format', False)

        if self.format == 'csv':
            return ExportCSV(
                self, self.get_queryset()
            )

        return super(ClientList, self).get(request, **kwargs)


def ExportCSV(self, queryset):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] =\
        'attachment; filename=client_export.csv'
    writer = csv.writer(response, csv.excel)
    writer.writerow([
        "ID",
        "Client Firstname",
        "Client Lastname",
        "Client Status",
        "Client Alert",
        "Client Gender",
        "Client Birthdate",
        "Client Delivery",
        "Client Home Phone",
        "Client Cell Phone",
        "Client Work Phone",
        "Client Email",
        "Client Street",
        "Client Apartment",
        "Client City",
        "Client Postal Code",
        "Client Route",
        "Client Billing Type",
        "Billing Firstname",
        "Billing Lastname",
        "Billing Street",
        "Billing Apartment",
        "Billing City",
        "Billing Postal Code",
        "Emergency Contact Firstname",
        "Emergency Contact Lastname",
        "Emergency Contact Home Phone",
        "Emergency Contact Cell Phone",
        "Emergency Contact Work Phone",
        "Emergency Contact Email",
        "Emergency Contact Relationship",
        "Meal Default",
    ])

    for obj in queryset:
        if obj.route is None:
            route = ""

        else:
            route = obj.route.name

        writer.writerow([
            obj.id,
            obj.member.firstname,
            obj.member.lastname,
            obj.get_status_display(),
            obj.alert,
            obj.gender,
            obj.birthdate,
            obj.delivery_type,
            obj.member.home_phone,
            obj.member.cell_phone,
            obj.member.work_phone,
            obj.member.email,
            obj.member.address.street,
            obj.member.address.apartment,
            obj.member.address.city,
            obj.member.address.postal_code,
            route,
            obj.billing_payment_type,
            obj.billing_member.firstname,
            obj.billing_member.lastname,
            obj.billing_member.address.street,
            obj.billing_member.address.apartment,
            obj.billing_member.address.city,
            obj.billing_member.address.postal_code,
            obj.emergency_contact.firstname,
            obj.emergency_contact.lastname,
            obj.emergency_contact.home_phone,
            obj.emergency_contact.cell_phone,
            obj.emergency_contact.work_phone,
            obj.emergency_contact.email,
            obj.emergency_contact_relationship,
            obj.meal_default_week,
        ])

    return response


class ClientInfoView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/information.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientInfoView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientInfoView, self).get_context_data(**kwargs)
        context['active_tab'] = 'information'
        context['client_status'] = Client.CLIENT_STATUS
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
        context['active_tab'] = 'referent'
        context['client_status'] = Client.CLIENT_STATUS
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
        context['active_tab'] = 'billing'
        context['client_status'] = Client.CLIENT_STATUS
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
        context['active_tab'] = 'prefs'
        context['client_status'] = Client.CLIENT_STATUS
        
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


class ClientStatusView(generic.DetailView):
    model = Client
    template_name = 'client/view/status.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientStatusView, self).dispatch(*args, **kwargs)

    def get_default_ops_value(self):
        operation_status_value = self.request.GET.get(
            'operation_status', ClientScheduledStatus.TOBEPROCESSED)
        if operation_status_value == ClientScheduledStatusFilter.ALL:
            operation_status_value = None
        return operation_status_value

    def get_context_data(self, **kwargs):
        context = super(ClientStatusView, self).get_context_data(**kwargs)
        context['active_tab'] = 'status'
        context['client_status'] = Client.CLIENT_STATUS
        context['filter'] = ClientScheduledStatusFilter(
            {'operation_status': self.get_default_ops_value()},
            queryset=self.object.scheduled_statuses)
        context['client_statuses'] = context['filter'].qs

        return context


class ClientNotesView(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view/notes.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientNotesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientNotesView, self).get_context_data(**kwargs)
        context['active_tab'] = 'notes'
        context['notes'] = NoteClientFilter(
            self.request.GET, queryset=self.object.notes).qs

        uf = NoteClientFilter(self.request.GET, queryset=self.object.notes)
        context['filter'] = uf

        return context


def note_add(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            model_instance = form.save(commit=False)
            model_instance.author = request.user
            model_instance.save()
            return render(request, 'notes/add.html', {'form': form})
    else:
        form = NoteForm()

    return render(request, 'notes/add.html', {'form': form})


def parse_json(meals):
    meal_default = []

    for meal in meals:
        if meals[meal] is not None:
            meal_default.append(meal + ": " + str(meals[meal]))

    return meal_default


class ClientDetail(generic.DetailView):
    # Display detail of one client
    model = Client
    template_name = 'client/view.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientDetail, self).get_context_data(**kwargs)
        context['notes'] = list(Note.objects.all())
        if self.object.meal_default_week:
            context['meal_default'] = parse_json(self.object.meal_default_week)
        else:
            context['meal_default'] = []
        return context


class ClientOrderList(generic.DetailView):
    # Display the list of clients
    model = Client
    template_name = 'client/view/orders.html'

    def get_context_data(self, **kwargs):

        context = super(ClientOrderList, self).get_context_data(**kwargs)
        context['orders'] = self.object.orders
        context['client_status'] = Client.CLIENT_STATUS
        context['active_tab'] = 'orders'
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


class SearchMembers(generic.View):

    def get(self, request):
        if request.is_ajax():
            q = self.request.GET.get('name', '')
            name_contains = Q()
            firstname_contains = Q(
                firstname__icontains=q
            )
            lastname_contains = Q(
                lastname__icontains=q
            )
            name_contains |= firstname_contains | lastname_contains
            members = Member.objects.filter(name_contains)[:20]
            results = []
            for m in members:
                name = '[' + str(m.id) + '] ' + m.firstname + ' ' + m.lastname
                results.append({'title': name})
            data = {
                'success': True,
                'results': results
            }
        else:
            data = {'success': False}

        return JsonResponse(data)


def geolocateAddress(request):
            # do something with the your data
    if request.method == 'POST':
        lat = request.POST['lat']
        long = request.POST['long']

    # just return a JsonResponse
    return JsonResponse({'latitude': lat, 'longtitude': long})


class ClientStatusScheduler(generic.CreateView, AjaxableResponseMixin):
    model = ClientScheduledStatus
    form_class = ClientScheduledStatusForm
    template_name = "client/update/status.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientStatusScheduler, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ClientStatusScheduler, self).get_context_data(**kwargs)
        context['client'] = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        context['client_status'] = Client.CLIENT_STATUS
        return context

    def get_initial(self):
        client = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        return {
            'client': self.kwargs.get('pk'),
            'status_from': client.status,
            'status_to': self.request.GET.get('status', Client.PAUSED),
        }

    def form_valid(self, form):
        client = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        start_date = form.cleaned_data.get('change_date')
        end_date = form.cleaned_data.get('end_date')

        response = super(ClientStatusScheduler, self).form_valid(form)

        # Immediate status update (schedule and process)
        if start_date == date.today():
            self.object.process()

        # Schedule a time range during which status will be different,
        # then back to current (double schedule)
        if end_date is not None:
            change2 = ClientScheduledStatus(
                client=client,
                status_from=form.cleaned_data.get('status_to'),
                status_to=form.cleaned_data.get('status_from'),
                reason=form.cleaned_data.get('reason'),
                change_date=end_date,
                change_state=ClientScheduledStatus.END,
                operation_status=ClientScheduledStatus.TOBEPROCESSED
            )
            change2.linked_scheduled_status = self.object
            change2.save()

        return response

    def get_success_url(self):
        return reverse_lazy(
            'member:client_information', kwargs={'pk': self.kwargs.get('pk')}
        )


class DeleteRestriction(generic.DeleteView):
    model = Restriction
    success_url = reverse_lazy('member:list')


class DeleteClientOption(generic.DeleteView):
    model = Client_option
    success_url = reverse_lazy('member:list')


class DeleteIngredientToAvoid(generic.DeleteView):
    model = Client_avoid_ingredient
    success_url = reverse_lazy('member:list')


class DeleteComponentToAvoid(generic.DeleteView):
    model = Client_avoid_component
    success_url = reverse_lazy('member:list')
