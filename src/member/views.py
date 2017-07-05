# coding: utf-8

import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.urls import reverse_lazy, reverse
from django.db import transaction
from django.db.models import Q, Prefetch, When, Case, Sum, IntegerField
from django.db.transaction import atomic
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator, classonlymethod
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from formtools.wizard.views import NamedUrlSessionWizardView

from delivery.views import calculateRoutePointsEuclidean
from meal.models import COMPONENT_GROUP_CHOICES, COMPONENT_GROUP_CHOICES_SIDES
from member.forms import (
    ClientScheduledStatusForm,
    ClientBasicInformation,
    ClientAddressInformation,
    ClientRestrictionsInformation,
    ClientPaymentInformation,
)
from member.formsets import (CreateRelationshipFormset,
                             UpdateRelationshipFormset)
from member.models import (
    Client,
    ClientScheduledStatus,
    Route, DeliveryHistory,
    Member,
    Address,
    Contact,
    Restriction,
    Relationship,
    Client_option,
    ClientFilter,
    ClientScheduledStatusFilter,
    DAYS_OF_WEEK,
    Client_avoid_ingredient,
    Client_avoid_component,
    HOME, WORK, CELL, EMAIL)
from note.models import Note
from order.mixins import FormValidAjaxableResponseMixin
from order.models import SIZE_CHOICES, Order


class NamedUrlSessionWizardView_i18nURL(NamedUrlSessionWizardView):

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        cls.i18n_url_names = kwargs.pop('i18n_url_names')
        return super(NamedUrlSessionWizardView_i18nURL, cls).as_view(
            *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Replace kwargs['step'] as non-i18n step name.
        """
        if 'step' in kwargs:
            i18n_step = kwargs.pop('step')
            try:
                matched_tup = next(
                    tup for tup in self.i18n_url_names
                    if force_text(tup[1]) == i18n_step
                )
                non_i18n_step = matched_tup[0]
            except StopIteration:
                # not found
                non_i18n_step = i18n_step
            finally:
                kwargs['step'] = non_i18n_step
        return super(NamedUrlSessionWizardView_i18nURL, self).dispatch(
            request, *args, **kwargs)

    def get_step_url(self, step):
        """
        Replace non-i18n step name as i18n step name.
        """
        non_i18n_step = step
        try:
            matched_tup = next(
                tup for tup in self.i18n_url_names
                if force_text(tup[0]) == non_i18n_step
            )
            i18n_step = matched_tup[1]
        except StopIteration:
            # not found
            i18n_step = non_i18n_step
        finally:
            return super(NamedUrlSessionWizardView_i18nURL, self).get_step_url(
                i18n_step)


class ClientWizard(
        LoginRequiredMixin, PermissionRequiredMixin,
        NamedUrlSessionWizardView_i18nURL):
    permission_required = 'sous_chef.edit'
    template_name = 'client/create/form.html'

    def get_context_data(self, **kwargs):
        context = super(ClientWizard, self).get_context_data(**kwargs)

        context["weekday"] = DAYS_OF_WEEK
        context["meals"] = list(filter(
            lambda tup: tup[0] != COMPONENT_GROUP_CHOICES_SIDES,
            COMPONENT_GROUP_CHOICES
        ))

        if 'pk' in kwargs:
            context.update({'edit': True})
            context.update({'pk': kwargs['pk']})

        form = context['form']
        if isinstance(form, ClientBasicInformation):
            step_template = 'client/partials/forms/basic_information.html'
        elif isinstance(form, ClientAddressInformation):
            step_template = 'client/partials/forms/address_information.html'
        elif isinstance(form, ClientPaymentInformation):
            step_template = 'client/partials/forms/payment_information.html'
        elif isinstance(form, ClientRestrictionsInformation):
            step_template = 'client/partials/forms/dietary_restriction.html'
        elif isinstance(form, CreateRelationshipFormset):
            step_template = 'client/partials/forms/relationships.html'
        else:
            step_template = None
        context['step_template'] = step_template

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
                if meal is COMPONENT_GROUP_CHOICES_SIDES:
                    continue  # skip "Sides"
                json['{}_{}_quantity'.format(meal, days)] \
                    = dictonary.get(
                    '{}_{}_quantity'.format(meal, days)
                )

        return json

    @atomic
    def save(self, id=None):
        """
        Update or create the member and all its related data.
        """
        basic_information = self.form_dict['basic_information'].cleaned_data
        address_information = self.form_dict[
            'address_information'].cleaned_data
        relationships = self.form_dict[
            'relationships'].cleaned_data
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
                'delivery_type': dietary_restriction.get('delivery_type'),
                'meal_default_week': self.save_json(dietary_restriction),
                'route': address_information.get('route'),
                'delivery_note': address_information.get('delivery_note'),
                'status': 'A' if dietary_restriction['status'] else 'D',
            }
        )

        self.save_relationships(billing_member, client)
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

    def save_relationships(self, billing_member, client):
        relationships = self.form_dict['relationships']
        results = []
        for relationship in relationships:
            # Avoid empty forms, at least one relationship form is
            # required by django formset validation. If we have
            # one form good filled and several empty forms, the 'is_valid'
            # method return True
            if relationship.changed_data:
                data = relationship.cleaned_data
                relationship_member = data.get('member')
                if self.billing_member_is_relationship(
                        relationship, billing_member):
                    member = billing_member
                elif relationship_member:
                    relationship_member_id = relationship_member.split(' ')[0]\
                        .replace('[', '')\
                        .replace(']', '')
                    member = Member.objects.get(pk=relationship_member_id)
                else:
                    member = Member.objects.create(
                        firstname=data.get("firstname"),
                        lastname=data.get('lastname')
                    )
                    if relationship.has_referent_relationship:
                        member.work_information = data.get('work_information')
                    member.save()
                    r_email = data.get("email", None)
                    r_work_phone = data.get("work_phone", None)
                    r_cell_phone = data.get("cell_phone", None)
                    if r_email:
                        member.add_contact_information(EMAIL, r_email)
                    if r_work_phone:
                        member.add_contact_information(WORK, r_work_phone)
                    if r_cell_phone:
                        member.add_contact_information(CELL, r_cell_phone)

                extra_fields = {}
                if relationship.has_referent_relationship:
                    extra_fields[
                        'referral_date'] = data.get('referral_date')
                    extra_fields[
                        'referral_reason'] = data.get('referral_reason')

                results.append(Relationship.objects.create(
                    client=client,
                    member=member,
                    nature=data.get('nature'),
                    type=data.get('type'),
                    remark=data.get('remark'),
                    extra_fields=extra_fields
                ))

        return results

    def save_preferences(self, client):
        preferences = self.form_dict['dietary_restriction'].cleaned_data

        # Save meals schedule as a Client option
        client.set_simple_meals_schedule(
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

    def billing_member_is_relationship(
            self, relationship, billing_member
    ):
        r_firstname = relationship.cleaned_data.get('firstname')
        r_lastname = relationship.cleaned_data.get('lastname')

        if (
            r_firstname == billing_member.firstname and
            r_lastname == billing_member.lastname
        ):
            return True

        return False


class ClientList(
        LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    # Display the list of clients
    context_object_name = 'clients'
    model = Client
    paginate_by = 20
    permission_required = 'sous_chef.read'
    template_name = 'client/list.html'

    def get_queryset(self):
        uf = ClientFilter(self.request.GET)
        return uf.qs.select_related(
            'member',
            'route'
        ).prefetch_related('member__member_contact')

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
        "Billing Member",
        "Relationships",
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
            obj.billing_member,
            ", ".join(str(c) for c in obj.relationships.all()),
            obj.meal_default_week,
        ])

    return response


class ClientView(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    # Display detail of one client
    model = Client
    queryset = Client.objects.prefetch_related(Prefetch(
        'scheduled_statuses',
        queryset=ClientScheduledStatus.objects.filter(
            operation_status__in=[
                ClientScheduledStatus.TOBEPROCESSED,
                ClientScheduledStatus.ERROR
            ]).order_by('change_date'),
        to_attr='unprocessed_scheduled_statuses'))
    permission_required = 'sous_chef.read'


class ClientInfoView(ClientView):
    template_name = 'client/view/information.html'

    def get_context_data(self, **kwargs):
        context = super(ClientInfoView, self).get_context_data(**kwargs)
        context['active_tab'] = 'information'
        context['client_status'] = Client.CLIENT_STATUS
        return context


class ClientAddressView(ClientView):
    template_name = 'client/view/address.html'

    def get_context_data(self, **kwargs):
        context = super(ClientAddressView, self).get_context_data(**kwargs)
        return context


class ClientPaymentView(ClientView):
    template_name = 'client/view/payment.html'

    def get_context_data(self, **kwargs):
        context = super(ClientPaymentView, self).get_context_data(**kwargs)
        context['active_tab'] = 'billing'
        context['client_status'] = Client.CLIENT_STATUS
        return context


class ClientAllergiesView(ClientView):
    template_name = 'client/view/allergies.html'

    def get_context_data(self, **kwargs):
        context = super(ClientAllergiesView, self).get_context_data(**kwargs)
        context['active_tab'] = 'prefs'
        context['client_status'] = Client.CLIENT_STATUS
        context['weekdays'] = DAYS_OF_WEEK
        sms = self.object.simple_meals_schedule
        if sms:
            weekdays_dict = dict(DAYS_OF_WEEK)
            context['delivery_days'] = list(map(
                lambda d: (d, weekdays_dict[d]), sms
            ))

        context['components'] = list(filter(
            lambda t: t[0] != COMPONENT_GROUP_CHOICES_SIDES,
            COMPONENT_GROUP_CHOICES
        ))
        context['meals_default'] = dict(self.object.meals_default)
        context['size_choices'] = dict(SIZE_CHOICES)
        return context


class ClientStatusView(ClientView):
    template_name = 'client/view/status.html'

    def get_default_ops_value(self):
        return self.request.GET.get('operation_status', None)

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
        context['orders'] = self.object.orders.prefetch_related(
            'orders'
        )
        context['client_status'] = Client.CLIENT_STATUS
        context['active_tab'] = 'orders'
        return context


class ClientUpdateInformation(
        LoginRequiredMixin, PermissionRequiredMixin,
        generic.edit.FormView):
    permission_required = 'sous_chef.edit'
    template_name = 'client/update/steps.html'

    def get_initial(self):
        client = get_object_or_404(
            Client.objects.select_related(
                'route',
                'member__address'
            ).prefetch_related('member__member_contact'),
            pk=self.kwargs.get('pk')
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
        }
        return initial

    def get_success_url(self):
        redirect_url = self.request.GET.get('next')
        if redirect_url:
            return redirect_url
        else:
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
        context["meals"] = list(filter(
            lambda tup: tup[0] != COMPONENT_GROUP_CHOICES_SIDES,
            COMPONENT_GROUP_CHOICES
        ))
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
        for k, v in (client.meal_default_week or {}).items():
            initial[k] = v
        return initial

    def save(self, form, client):
        """
        Save the basic information step data.
        """
        # Save meals schedule as a Client option
        client.set_simple_meals_schedule(
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

            for meal, Meal in COMPONENT_GROUP_CHOICES:
                if meal is COMPONENT_GROUP_CHOICES_SIDES:
                    continue  # skip "Sides"
                json['{}_{}_quantity'.format(meal, days)] \
                    = form[
                    '{}_{}_quantity'.format(meal, days)
                ]
        client.delivery_type = form['delivery_type']
        client.meal_default_week = json
        client.save()


class ClientUpdateRelationshipsInformation(ClientUpdateInformation):
    form_class = UpdateRelationshipFormset
    prefix = 'relationships'

    def get_context_data(self, **kwargs):
        context = super(
            ClientUpdateRelationshipsInformation,
            self).get_context_data(
            **kwargs)
        context.update({'current_step': 'relationships'})
        context.update({'pk': self.kwargs['pk']})
        context["step_template"] = 'client/partials/forms/' \
                                   'relationships.html'
        return context

    def get_initial(self):
        client = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        initial = {}

        if self.request.method == 'GET':
            for i, relationship in enumerate(
                    client.relationship_set.all()
            ):
                contact = relationship.member.member_contact.first()
                if contact:
                    contact_type = contact.type
                    contact_value = contact.value
                else:
                    contact_type = None
                    contact_value = None

                initial[i] = {
                    'firstname': None,
                    'lastname': None,
                    'member': '[{}] {} {}'.format(
                        relationship.member.id,
                        relationship.member.firstname,
                        relationship.member.lastname
                    ),
                    'contact_type': contact_type,
                    'contact_value': contact_value,
                    'nature': relationship.nature,
                    'type': relationship.type,
                    'remark': relationship.remark
                }
                if relationship.is_referent:
                    initial[i]['referral_date'] = \
                        relationship.extra_fields.get('referral_date')
                    initial[i]['referral_reason'] = \
                        relationship.extra_fields.get('referral_reason')

        return initial

    def save(self, relationships, client):
        """
        Save relationships data.
        """
        relationships_posted = []
        for relationship in relationships:
            # Avoid empty forms, at least one relationship form is
            # required by django formset validation. If we have
            # one form good filled and several empty forms, the 'is_valid'
            # method return True
            if relationship:
                r_member = relationship.get('member')
                if r_member:
                    r_member_id = r_member.split(' ')[0] \
                        .replace('[', '') \
                        .replace(']', '')
                    member = Member.objects.get(pk=r_member_id)
                else:
                    member = Member.objects.create(
                        firstname=relationship.get("firstname"),
                        lastname=relationship.get('lastname'),
                    )
                    if Relationship.REFERENT in relationship.get('type', []):
                        member.work_information = relationship.get(
                            'work_information')
                    member.save()

                    # save emergency contact
                    if relationship.get('work_phone'):
                        Contact.objects.create(
                            type=WORK,
                            value=relationship.get('work_phone'),
                            member=member
                        )
                    elif relationship.get('cell_phone'):
                        Contact.objects.create(
                            type=CELL,
                            value=relationship.get('cell_phone'),
                            member=member
                        )
                    elif relationship.get('home_phone'):
                        Contact.objects.create(
                            type=HOME,
                            value=relationship.get('home_phone'),
                            member=member
                        )
                    elif relationship.get('email'):
                        Contact.objects.create(
                            type=EMAIL,
                            value=relationship.get('email'),
                            member=member
                        )

                to_update, _ = Relationship.objects.get_or_create(
                    client=client, member=member)
                to_update.nature = relationship.get('nature')
                to_update.type = relationship.get('type')
                extra_fields = {}
                if Relationship.REFERENT in relationship.get('type', []):
                    extra_fields[
                        'referral_date'] = relationship.get('referral_date')
                    extra_fields[
                        'referral_reason'] = relationship.get(
                            'referral_reason')
                to_update.extra_fields = extra_fields
                to_update.remark = relationship.get('remark')
                to_update.save()
                relationships_posted.append(to_update)

        Relationship.objects.filter(client=client).exclude(
            pk__in=[c.pk for c in relationships_posted]
        ).delete()


class SearchMembers(LoginRequiredMixin, PermissionRequiredMixin, generic.View):
    permission_required = 'sous_chef.read'

    @staticmethod
    def _get_query_args(query):
        """
        Return query arguments built for first_name and
        last_name Member fields
        :return: Q() | Q() or Q() & Q()
        """
        query = query.strip()
        if ' ' not in query:
            # Is a simple word, check if both fields contains
            # the query value
            return Q(
                firstname__icontains=query
            ) | Q(
                lastname__icontains=query
            )
        else:
            # More than one word, split query to search separately
            # by first and last name
            s_query = query.split(' ')
            return Q(
                firstname__icontains=s_query[0]
            ) & Q(
                lastname__icontains=' '.join(s_query[1:])
            )

    def get(self, request):
        if request.is_ajax():
            q = request.GET.get('name', '')
            members = Member.objects.filter(self._get_query_args(q))[:20]
            results = []
            for m in members:
                name = '[' + str(m.id) + '] ' + m.firstname + ' ' + m.lastname

                if m.work_information is not None:
                    name += ' (' + m.work_information + ')'

                results.append({'title': name})
            data = {
                'success': True,
                'results': results
            }
        else:
            data = {'success': False}

        return JsonResponse(data)


@login_required
def geolocateAddress(request):
    # do something with the your data
    if request.method == 'POST':
        lat = request.POST['lat']
        long = request.POST['long']

    # just return a JsonResponse
    return JsonResponse({'latitude': lat, 'longtitude': long})


class ClientStatusScheduler(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        FormValidAjaxableResponseMixin,
        generic.CreateView
):
    form_class = ClientScheduledStatusForm
    model = ClientScheduledStatus
    permission_required = 'sous_chef.edit'
    template_name = "client/update/status.html"

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
        """
        Override the default behavior of saving instance, because we may have
        two objects to save.
        """
        form.save_scheduled_statuses(
            callback_add_message=lambda m: messages.add_message(
                self.request, messages.SUCCESS, m))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'member:client_information', kwargs={'pk': self.kwargs.get('pk')}
        )


class ClientStatusSchedulerReschedule(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        FormValidAjaxableResponseMixin,
        generic.UpdateView
):
    form_class = ClientScheduledStatusForm
    model = ClientScheduledStatus
    permission_required = 'sous_chef.edit'
    template_name = "client/update/status.html"

    def dispatch(self, *args, **kwargs):
        """
        Fetch related objects at the very beginning of request process.
        """
        self.cs1 = get_object_or_404(
            ClientScheduledStatus, pk=int(
                self.kwargs.get('scheduled_status_1_pk')))

        if self.kwargs.get('scheduled_status_2_pk'):
            try:
                self.cs2 = ClientScheduledStatus.objects.get(
                    pk=int(self.kwargs.get('scheduled_status_2_pk')))
                if self.cs2.get_pair != self.cs1:
                    self.cs2 = None  # Ignore
            except ClientScheduledStatus.DoesNotExist:
                self.cs2 = None
        else:
            self.cs2 = None
        return super().dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = get_object_or_404(
            Client, pk=self.kwargs.get('pk')
        )
        context['client_status'] = Client.CLIENT_STATUS
        return context

    def get_initial(self):
        return {
            'client': self.kwargs.get('pk'),
            'status_from': self.cs1.status_from,
            'status_to': self.cs1.status_to,
            'reason': self.cs1.reason,
            'change_date': self.cs1.change_date,
            'end_date': self.cs2.change_date if self.cs2 else None
        }

    def form_valid(self, form):
        """
        Replace original ClientScheduledStatus objects.
        """
        # Unbind pairs and delete
        with transaction.atomic():
            self.cs1.delete()
            if self.cs2:
                self.cs2.delete()

        form.save_scheduled_statuses(
            callback_add_message=lambda m: messages.add_message(
                self.request, messages.SUCCESS, m))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'member:client_information', kwargs={'pk': self.kwargs.get('pk')}
        )


class ClientStatusSchedulerDeleteView(
        PermissionRequiredMixin, generic.DeleteView):
    model = ClientScheduledStatus
    permission_required = 'sous_chef.edit'
    template_name = "client/view/delete_status_confirmation.html"

    def get_success_url(self):
        return reverse(
            'member:client_status',
            kwargs={'pk': self.object.client.pk}
        )


class DeleteRestriction(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Restriction
    permission_required = 'sous_chef.edit'
    success_url = reverse_lazy('member:list')


class DeleteClientOption(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Client_option
    permission_required = 'sous_chef.edit'
    success_url = reverse_lazy('member:list')


class DeleteIngredientToAvoid(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Client_avoid_ingredient
    permission_required = 'sous_chef.edit'
    success_url = reverse_lazy('member:list')


class DeleteComponentToAvoid(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Client_avoid_component
    permission_required = 'sous_chef.edit'
    success_url = reverse_lazy('member:list')


class RouteListView(
        LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    # Display the list of routes
    context_object_name = 'routes'
    model = Route
    queryset = Route.objects.all().annotate(
        client_count=Sum(
            Case(
                When(client__status__in=[
                    Client.PENDING, Client.ACTIVE, Client.PAUSED],
                     then=1),
                default=0,
                output_field=IntegerField()
            )
        )
    )
    permission_required = 'sous_chef.read'
    template_name = 'route/list.html'


def get_clients_on_route(route):
    """
    Helper function, intended to generate the context variable of
    Route-related views.

    Returns a list of client instances with an extra attribute
    `has_been_configured`, ordered by configured then unconfigured.
    """
    clients = Client.objects. \
        filter(route=route,
               status__in=[
                   Client.PENDING, Client.ACTIVE, Client.PAUSED]). \
        select_related('member', 'member__address')
    clients_dict = {client.pk: client for client in clients}
    clients_on_route = []
    for client_pk in (route.client_id_sequence or []):
        if client_pk in clients_dict:
            client = clients_dict[client_pk]
            client.has_been_configured = True
            clients_on_route.append(client)
            del clients_dict[client_pk]
        else:
            # This client has been deleted after configuring the route.
            # We don't include it in the sequence. Thus, when the user updates
            # the default route sequence the next time, everything will be OK.
            pass

    for client_pk, client in clients_dict.items():
        # Remaining clients
        client.has_been_configured = False
        clients_on_route.append(client)

    return clients_on_route


def get_clients_on_delivery_history(
        delivery_history, func_add_warning_message=None):
    """
    Helper function, intended to generate the context variable of
    DeliveryHistory-related views.

    Returns a list of client instances with extra attributes
    `has_been_configured` and `order_of_the_day`, ordered by configured
    then unconfigured.

    `order_of_the_day` could be none if we can't find the order and the
    client is on the sequence. We assume that the order was deleted.

    `func_add_warning_message` accepts one single string-like parameter.
    It is called when we find a data integrity problem. That is when
    there's a client that doesn't exist or we can't find his order
    on that day any more.

    See also: member.tests.RouteDeliveryHistoryDetailViewTestCase
    """
    orders = Order.objects.get_shippable_orders_by_route(
        delivery_history.route.pk,
        delivery_date=delivery_history.date,
        exclude_non_geolocalized=True
    ).select_related(
        'client', 'client__member',
        'client__member__address'
    )
    clients = []
    clients_dict = {}
    for order in orders:
        c = order.client
        c.order_of_the_day = order
        clients.append(c)
        clients_dict[c.pk] = c

    clients_on_delivery_history = []

    # First, check the clients on `id_sequence` and see if we put them in the
    # display sequence.
    for client_pk in (delivery_history.client_id_sequence or []):
        if client_pk in clients_dict:
            client = clients_dict[client_pk]
            client.has_been_configured = True
            clients_on_delivery_history.append(client)
            del clients_dict[client_pk]
        else:
            # Oops, a data integrity error. Let user know.
            if func_add_warning_message:
                try:
                    client = Client.objects.select_related('member').get(
                        pk=int(client_pk))
                    func_add_warning_message(mark_safe(_(
                        "The client <a href=%(url)s>%(firstname)s %(lastname)s"
                        "</a> is found on this delivery sequence but is no "
                        "longer valid for this delivery." % {
                            'firstname': client.member.firstname,
                            'lastname': client.member.lastname,
                            'url': reverse('member:client_information',
                                           args=(client.pk, ))
                        })))
                except (Client.DoesNotExist, ValueError, TypeError):
                    func_add_warning_message(_(
                        "The delivery sequence contains a client with ID"
                        "%(client_id)s that no longer exists in the "
                        "database." % {
                            'client_id': client_pk
                        }))

    # Then, check if there are clients that exist on default route sequence.
    # They are considered as "by default".
    for cpk in (delivery_history.route.client_id_sequence or []):
        if cpk in clients_dict:
            client = clients_dict[cpk]
            client.has_been_configured = False
            clients_on_delivery_history.append(client)
            del clients_dict[cpk]

    # Finally, check the clients that had delivery on that day but were not
    # configured on the delivery sequence. Append them to the display sequence.
    for client_pk, client in clients_dict.items():
        client.has_been_configured = False
        clients_on_delivery_history.append(client)
    return clients_on_delivery_history


class RouteDetailView(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = Route
    queryset = Route.objects.prefetch_related(Prefetch(
        'delivery_histories',
        queryset=DeliveryHistory.objects.order_by('-date')
    ))
    permission_required = 'sous_chef.read'
    template_name = 'route/detail.html'

    def get_context_data(self, **kwargs):
        """
        Get detailed information on route clients and out-of-route clients
        that are to be rendered on the template.
        """
        context = super(RouteDetailView, self).get_context_data(**kwargs)
        route = context['route']
        context['clients_on_route'] = get_clients_on_route(route)
        return context


class RouteEditView(
        LoginRequiredMixin, PermissionRequiredMixin, generic.edit.UpdateView):
    model = Route
    fields = ('name', 'description', 'vehicle', 'client_id_sequence')
    permission_required = 'sous_chef.edit'
    template_name = 'route/edit.html'

    def get_context_data(self, **kwargs):
        """
        Get detailed information on route clients and out-of-route clients
        that are to be rendered on the template.
        """
        context = super(RouteEditView, self).get_context_data(**kwargs)
        route = context['route']
        context['clients_on_route'] = get_clients_on_route(route)
        return context

    def get_success_url(self):
        return reverse_lazy('member:route_detail', args=[self.object.pk])

    def form_valid(self, form):
        response = super(RouteEditView, self).form_valid(form)
        messages.add_message(
            self.request, messages.SUCCESS,
            _("This route has been updated.")
        )
        return response


@login_required
def get_minimised_euclidean_distances_route_sequence(request, pk):
    """
    Return the sequence of clients on the given route that minimises
    euclidean distances, as a JSON list of client IDs.
    """
    route = get_object_or_404(Route, pk=pk)
    clients_on_route = get_clients_on_route(route)
    waypoints = list(map(
        lambda c: {
            'id': c.pk,
            'latitude': c.member.address.latitude,
            'longitude': c.member.address.longitude
        }, clients_on_route
    ))
    optimised_waypoints = calculateRoutePointsEuclidean(waypoints)
    return JsonResponse(
        list(map(lambda w: w['id'], optimised_waypoints)),
        safe=False
    )


class DeliveryHistoryDetailView(
        LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
    model = DeliveryHistory
    permission_required = 'sous_chef.read'
    template_name = 'route/delivery_history_detail.html'

    def get_object(self, *args, **kwargs):
        return DeliveryHistory.objects.select_related('route').get(
            route=self.kwargs.get('route_pk'),
            date=self.kwargs.get('date')
        )

    def get_context_data(self, **kwargs):
        """
        Get detailed information on route clients and out-of-route clients
        that are to be rendered on the template.
        """
        context = super(
            DeliveryHistoryDetailView, self
        ).get_context_data(**kwargs)
        delivery_history = self.object
        context['delivery_history'] = delivery_history
        context['clients_on_delivery_history'] = (
            get_clients_on_delivery_history(
                delivery_history,
                func_add_warning_message=lambda msg: messages.add_message(
                    self.request, messages.WARNING, msg)
            )
        )
        return context
