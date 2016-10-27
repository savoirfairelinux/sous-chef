# coding: utf-8


import csv
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from formtools.wizard.views import NamedUrlSessionWizardView
from meal.models import COMPONENT_GROUP_CHOICES
from member.forms import (
    ClientScheduledStatusForm,
    ClientBasicInformation,
    ClientAddressInformation,
    ClientReferentInformation,
    ClientRestrictionsInformation,
    ClientPaymentInformation,
    ClientEmergencyContactInformation
)
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
    Client_avoid_ingredient,
    Client_avoid_component,
    HOME, WORK, CELL, EMAIL,
)
from note.models import Note
from order.mixins import AjaxableResponseMixin


class ClientWizard(NamedUrlSessionWizardView):

    template_name = 'client/create/form.html'

    def get_context_data(self, **kwargs):
        context = super(ClientWizard, self).get_context_data(**kwargs)

        context["weekday"] = DAYS_OF_WEEK
        context["meals"] = COMPONENT_GROUP_CHOICES

        if 'pk' in kwargs:
            context.update({'edit': True})
            context.update({'pk': kwargs['pk']})

        return context

    def get_form_initial(self, step):
        """
        Load initial data.
        """
        initial = {}
        if 'pk' in self.kwargs:
            pk = self.kwargs['pk']
            client = Client.objects.get(id=pk)
            initial = self.load_initial_data(step, client)

        return self.initial_dict.get(step, initial)

    def done(self, form_list, form_dict, **kwargs):
        """
        Process the submitted and validated form data.
        """
        # Use form_dict which allows us to access the wizard’s forms
        # based on their step names.
        pk = None
        self.form_dict = form_dict

        if 'pk' in kwargs:
            pk = kwargs['pk']
        self.save(pk)
        messages.add_message(
            self.request, messages.SUCCESS,
            _("The client has been created")
        )
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
            'emergency_contact_relationship': '',
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
        emergency_information = self.form_dict[
            'emergency_contact'].cleaned_data

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

        member.add_contact_information(
            HOME, basic_information.get('home_phone')
        )
        member.add_contact_information(
            CELL, basic_information.get('cell_phone')
        )
        member.add_contact_information(
            EMAIL, basic_information.get('email')
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
                'emergency_contact_relationship':
                    emergency_information.get('relationship'),
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
            ref_email = referent_information.cleaned_data.get(
                "email", None)
            ref_work_phone = referent_information.cleaned_data.get(
                "work_phone", None)
            ref_cell_phone = referent_information.cleaned_data.get(
                "cell_phone", None)
            if ref_email:
                referent.add_contact_information(EMAIL, ref_email)
            if ref_work_phone:
                referent.add_contact_information(WORK, ref_work_phone)
            if ref_cell_phone:
                referent.add_contact_information(CELL, ref_cell_phone)

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


class ClientView(generic.DeleteView):
    # Display detail of one client
    model = Client

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ClientView, self).dispatch(*args, **kwargs)


class ClientInfoView(ClientView):
    template_name = 'client/view/information.html'

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


class ClientReferentView(ClientView):
    template_name = 'client/view/referent.html'

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


class ClientAddressView(ClientView):
    template_name = 'client/view/address.html'

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


class ClientPaymentView(ClientView):
    template_name = 'client/view/payment.html'

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


class ClientAllergiesView(ClientView):
    template_name = 'client/view/allergies.html'

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


class ClientStatusView(ClientView):
    template_name = 'client/view/status.html'

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


class ClientNotesView(ClientView):
    template_name = 'client/view/notes.html'

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


class ClientDetail(ClientView):
    template_name = 'client/view.html'

    def get_context_data(self, **kwargs):
        context = super(ClientDetail, self).get_context_data(**kwargs)
        context['notes'] = list(Note.objects.all())
        if self.object.meal_default_week:
            context['meal_default'] = parse_json(self.object.meal_default_week)
        else:
            context['meal_default'] = []
        return context

    def parse_json(meals):
        meal_default = []

        for meal in meals:
            if meals[meal] is not None:
                meal_default.append(meal + ": " + str(meals[meal]))

        return meal_default


class ClientOrderList(ClientView):
    template_name = 'client/view/orders.html'

    def get_context_data(self, **kwargs):

        context = super(ClientOrderList, self).get_context_data(**kwargs)
        context['orders'] = self.object.orders
        context['client_status'] = Client.CLIENT_STATUS
        context['active_tab'] = 'orders'
        return context


class ClientUpdateInformation(generic.edit.FormView):
    template_name = 'client/update/steps.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(
            ClientUpdateInformation,
            self).dispatch(
            *args,
            **kwargs)

    def get_initial(self):
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        initial = {
            'firstname': client.member.firstname,
            'lastname': client.member.lastname,
            'alert': client.alert,
            'gender': client.gender,
            'language': client.language,
            'birthdate': client.birthdate,
            'home_phone': client.member.home_phone,
            'cell_phone': client.member.cell_phone,
            'email': client.member.email,
            'street': client.member.address.street,
            'city': client.member.address.city,
            'apartment': client.member.address.apartment,
            'postal_code': client.member.address.postal_code,
            'delivery_note': client.delivery_note,
            'route':
                client.route.id
                if client.route is not None
                else '',
            'latitude': client.member.address.latitude,
            'longitude': client.member.address.longitude,
            'distance': client.member.address.distance,
            'work_information':
                client.client_referent.first().work_information
                if client.client_referent.count()
                else '',
            'referral_reason':
                client.client_referent.first().referral_reason
                if client.client_referent.count()
                else '',
            'date':
                client.client_referent.first().date
                if client.client_referent.count()
                else '',
        }
        return initial

    def get_success_url(self):
        return reverse_lazy(
            'member:client_information',
            kwargs={'pk': self.kwargs.get('pk')}
        )

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        self.save(form.cleaned_data, client)
        messages.add_message(
            self.request, messages.SUCCESS,
            _("The client has been updated")
        )
        return super(ClientUpdateInformation, self).form_valid(form)


class ClientUpdateBasicInformation(ClientUpdateInformation):
    form_class = ClientBasicInformation

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateBasicInformation,
            self).get_context_data(
            **kwargs)
        context.update({
            'pk': self.kwargs['pk'],
            'current_step': 'basic_information'
        })
        context["step_template"] = 'client/partials/forms/' \
                                   'basic_information.html'
        return context

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

        # Save contact information
        if client.member.home_phone != form['home_phone']:
            client.member.add_contact_information(
                HOME, form['home_phone'], True)
        if client.member.cell_phone != form['cell_phone']:
            client.member.add_contact_information(
                CELL, form['cell_phone'], True)
        if client.member.email != form['email']:
            client.member.add_contact_information(
                EMAIL, form['email'], True)


class ClientUpdateAddressInformation(ClientUpdateInformation):
    form_class = ClientAddressInformation

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateAddressInformation,
            self).get_context_data(
            **kwargs)
        context.update({
            'current_step': 'address_information',
            'pk': self.kwargs['pk']
        })
        context["step_template"] = 'client/partials/forms/' \
                                   'address_information.html'
        return context

    def save(self, form, client):
        """
        Save the basic information step data.
        """
        client.member.address.street = form['street']
        client.member.address.apartment = form['apartment']
        client.member.address.city = form['city']
        client.member.address.postal_code = form['postal_code']
        client.member.address.latitude = form['latitude']
        client.member.address.longitude = form['longitude']
        client.member.address.save()

        client.route = form['route']
        client.delivery_note = form['delivery_note']
        client.save()


class ClientUpdateReferentInformation(ClientUpdateInformation):
    form_class = ClientReferentInformation

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateReferentInformation,
            self).get_context_data(
            **kwargs)
        context.update({'current_step': 'referent_information'})
        context.update({'pk': self.kwargs['pk']})
        context["step_template"] = 'client/partials/forms/' \
                                   'referent_information.html'
        return context

    def get_initial(self):
        initial = super(ClientUpdateReferentInformation, self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        initial.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': None,
            'postal_code': None,
            'member': '[{}] {} {}'.format(
                client.client_referent.first().referent.id,
                client.client_referent.first().referent.firstname,
                client.client_referent.first().referent.lastname
            ),
        })
        return initial

    def save(self, referent_information, client):
        """
        Save the basic information step data.
        """
        e_referent = referent_information.get('member')
        if e_referent:
            e_referent_id = e_referent.split(' ')[0] \
                .replace('[', '') \
                .replace(']', '')
            referent = Member.objects.get(pk=e_referent_id)
        else:
            referent = Member.objects.create(
                firstname=referent_information.get("firstname"),
                lastname=referent_information.get("lastname"),
            )
            referent.save()

        # TODO: Find out if a client can really be refered by more
        # that one person in the system.
        # Before save a new referencing, remove the existing ones.
        Referencing.objects.filter(client=client).delete()

        referencing, updated = Referencing.objects.update_or_create(
            referent=referent,
            client=client,
            referral_reason=referent_information.get(
                "referral_reason"
            ),
            work_information=referent_information.get(
                'work_information'
            ),
            date=referent_information.get(
                'date'
            ),
        )
        referencing.save()


class ClientUpdatePaymentInformation(ClientUpdateInformation):
    form_class = ClientPaymentInformation

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdatePaymentInformation,
            self).get_context_data(
            **kwargs)
        context.update({
            'current_step': 'payment_information',
            'pk': self.kwargs['pk'],
        })
        context["step_template"] = 'client/partials/forms/' \
                                   'payment_information.html'
        return context

    def get_initial(self):
        initial = super(ClientUpdatePaymentInformation, self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        initial.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': None,
            'postal_code': None,
            'member': '[{}] {} {}'.format(
                client.billing_member.id,
                client.billing_member.firstname,
                client.billing_member.lastname
            ),
            'same_as_client': client.member == client.billing_member,
            'facturation': client.rate_type,
            'billing_payment_type': client.billing_payment_type,
        })

        return initial

    def save(self, payment_information, client):
        """
        Save the basic information step data.
        """
        member = client.member

        if payment_information.get('same_as_client'):
            billing_member = member

        else:
            e_b_member = payment_information.get('member')
            if e_b_member:
                e_b_member_id = e_b_member.split(' ')[0]. \
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
        client.billing_member = billing_member
        client.rate_type = payment_information.get('facturation')
        client.billing_payment_type = payment_information.get(
            'billing_payment_type'
        )
        client.save()


class ClientUpdateDietaryRestriction(ClientUpdateInformation):
    form_class = ClientRestrictionsInformation

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateDietaryRestriction,
            self).get_context_data(
            **kwargs)
        context.update({'current_step': 'dietary_restriction'})
        context.update({'pk': self.kwargs['pk']})
        context["weekday"] = DAYS_OF_WEEK
        context["meals"] = COMPONENT_GROUP_CHOICES
        context["step_template"] = 'client/partials/forms/' \
                                   'dietary_restriction.html'
        return context

    def get_initial(self):
        initial = super(ClientUpdateDietaryRestriction, self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        initial.update({
            'status': True if client.status == Client.ACTIVE else False,
            'delivery_type': client.delivery_type,
            'meals_schedule': client.simple_meals_schedule,
            'restrictions': client.restrictions.all,
            'ingredient_to_avoid': client.ingredients_to_avoid.all,
            'dish_to_avoid': client.components_to_avoid.all,
            'food_preparation': client.food_preparation.all,
        })
        day_count = 0
        for day, v in DAYS_OF_WEEK:
            for component, v in COMPONENT_GROUP_CHOICES:
                meals_default = Client.get_meal_defaults(
                    client, component, day_count)
                initial[component + '_' + day + '_quantity'] = meals_default[0]
                if component == 'main_dish':
                    initial['size_' + day] = meals_default[1]
            day_count += 1

        return initial

    def save(self, form, client):
        """
        Save the basic information step data.
        """
        # Save meals schedule as a Client option
        client.set_meals_schedule(
            form['meals_schedule']
        )

        # Save restricted items
        client.restrictions.clear()
        for restricted_item in form['restrictions']:
            Restriction.objects.create(
                client=client,
                restricted_item=restricted_item
            )

        for food_preparation in client.food_preparation:
            Client_option.objects.filter(
                client=client,
                option=food_preparation
            ).delete()
        for food_preparation in form['food_preparation']:
            Client_option.objects.create(
                client=client,
                option=food_preparation
            )

        # Save ingredients to avoid
        client.ingredients_to_avoid.clear()
        for ingredient_to_avoid in form['ingredient_to_avoid']:
            Client_avoid_ingredient.objects.create(
                client=client,
                ingredient=ingredient_to_avoid
            )

        # Save components to avoid
        client.components_to_avoid.clear()
        for component_to_avoid in form['dish_to_avoid']:
            Client_avoid_component.objects.create(
                client=client,
                component=component_to_avoid
            )

        # Save preferences
        json = {}
        for days, v in DAYS_OF_WEEK:
            json['size_{}'.format(days)] = form['size_{}'.format(days)]

            if json['size_{}'.format(days)] is "":
                json['size_{}'.format(days)] = None

            for meal in COMPONENT_GROUP_CHOICES:
                json['{}_{}_quantity'.format(meal[0], days)] \
                    = form[
                    '{}_{}_quantity'.format(meal[0], days)
                ]
        client.delivery_type = form['delivery_type']
        client.meal_default_week = json
        client.status = Client.ACTIVE if form.get('status') else Client.PENDING
        client.save()


class ClientUpdateEmergencyContactInformation(ClientUpdateInformation):
    form_class = ClientEmergencyContactInformation

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateEmergencyContactInformation,
            self).get_context_data(
            **kwargs)
        context.update({'current_step': 'emergency_contact'})
        context.update({'pk': self.kwargs['pk']})
        context["step_template"] = 'client/partials/forms/' \
                                   'emergency_contact.html'
        return context

    def get_initial(self):
        initial = super(ClientUpdateEmergencyContactInformation,
                        self).get_initial()
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        initial.update({
            'firstname': None,
            'lastname': None,
            'member': '[{}] {} {}'.format(
                client.emergency_contact.id,
                client.emergency_contact.firstname,
                client.emergency_contact.lastname
            ),
            'contact_type':
                client.emergency_contact.member_contact.first().type,
            'contact_value':
                client.emergency_contact.member_contact.first().value,
            'relationship':
                client.emergency_contact_relationship
        })
        return initial

    def save(self, emergency_contact, client):
        """
        Save the basic information step data.
        """
        e_emergency_member = emergency_contact.get('member')
        if e_emergency_member:
            e_emergency_member_id = e_emergency_member.split(' ')[0] \
                .replace('[', '') \
                .replace(']', '')
            emergency = Member.objects.get(pk=e_emergency_member_id)
        else:
            emergency = Member.objects.create(
                firstname=emergency_contact.get("firstname"),
                lastname=emergency_contact.get('lastname'),
            )
            emergency.save()

        # Remove old emergency_contact
        Contact.objects.filter(member=client.emergency_contact).delete()
        # Add new emergency_contact
        client_emergency_contact = Contact.objects.create(
            type=emergency_contact.get("contact_type"),
            value=emergency_contact.get(
                "contact_value"
            ),
            member=emergency,
        )
        client_emergency_contact.save()

        client.emergency_contact = emergency
        client.emergency_contact_relationship = emergency_contact.get(
            "relationship"
        )
        client.save()


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


class ClientStatusScheduler(AjaxableResponseMixin, generic.CreateView):
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
        messages.add_message(
            self.request, messages.SUCCESS,
            _("The status has been changed")
        )
        return response

    def get_success_url(self):
        return reverse(
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
