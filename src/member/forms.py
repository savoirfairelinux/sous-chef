from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from meal.models import Ingredient, Component, COMPONENT_GROUP_CHOICES, \
    Restricted_item
from order.models import SIZE_CHOICES
from member.models import (
    Member, Client, RATE_TYPE, CONTACT_TYPE_CHOICES, Option,
    GENDER_CHOICES, PAYMENT_TYPE, DELIVERY_TYPE,
    DAYS_OF_WEEK, Route, ClientScheduledStatus
)


class ClientBasicInformation (forms.Form):

    firstname = forms.CharField(
        max_length=100,
        label=_("First Name"),
        widget=forms.TextInput(attrs={'placeholder': _('First name')})
    )

    lastname = forms.CharField(
        max_length=100,
        label=_("Last Name"),
        widget=forms.TextInput(attrs={'placeholder': _('Last name')})
    )

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'ui dropdown'})
    )

    language = forms.ChoiceField(
        choices=Client.LANGUAGES,
        label=_("Preferred language"),
        widget=forms.Select(attrs={'class': 'ui dropdown'})
    )

    birthdate = forms.DateField(label=_("Birthday"))

    email = forms.CharField(
        label='<i class="email icon"></i>',
        widget=forms.TextInput(attrs={'placeholder': _('Email')}),
        required=False,
    )

    home_phone = forms.CharField(
        label='Home',
        widget=forms.TextInput(attrs={'placeholder': _('Home phone')}),
        required=False,
    )

    cell_phone = forms.CharField(
        label='Cell',
        widget=forms.TextInput(attrs={'placeholder': _('Cellular')}),
        required=False,
    )

    alert = forms.CharField(
        label=_("Alert"),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': _('Your message here ...')
        })
    )


class ClientAddressInformation(forms.Form):

    apartment = forms.IntegerField(
        label=_("Apt #"),
        widget=forms.TextInput(attrs={'placeholder': _('Apt #')}),
        required=False
    )

    street = forms.CharField(
        max_length=100,
        label=_("Address information"),
        widget=forms.TextInput(
            attrs={
                'placeholder': _('7275 Rue Saint-Urbain')}))

    city = forms.CharField(
        max_length=50,
        label=_("City"),
        widget=forms.TextInput(attrs={'placeholder': _('Montreal')})
    )

    postal_code = forms.CharField(
        max_length=6,
        label=_("Postal Code"),
        widget=forms.TextInput(attrs={'placeholder': _('H2R 2Y5')})
    )

    latitude = forms.CharField(
        label=_('Latitude'),
        required=False,
        initial=0,
        widget=forms.TextInput()
    )

    longitude = forms.CharField(
        label=_('Longitude'),
        required=False,
        initial=0,
        widget=forms.TextInput()
    )

    distance = forms.CharField(
        label=_('Distance from Santropol'),
        required=False,
        initial=0,
        widget=forms.TextInput()
    )

    route = forms.ModelChoiceField(
        label=_('Route'),
        required=True,
        widget=forms.Select(attrs={'class': 'ui search dropdown'}),
        queryset=Route.objects.all(),
    )

    delivery_note = forms.CharField(
        label=_("Delivery Note"),
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': _('Delivery Note here ...')
        })
    )


class ClientRestrictionsInformation(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ClientRestrictionsInformation, self).__init__(*args, **kwargs)

        for day, translation in DAYS_OF_WEEK:
            self.fields['size_{}'.format(day)] = forms.ChoiceField(
                choices=SIZE_CHOICES,
                widget=forms.Select(attrs={'class': 'ui dropdown'}),
                required=False
            )

            for meal, placeholder in COMPONENT_GROUP_CHOICES:
                self.fields['{}_{}_quantity'.format(meal, day)] = \
                    forms.IntegerField(
                        widget=forms.TextInput(
                            attrs={'placeholder': placeholder}
                        ),
                        required=False
                )

    status = forms.BooleanField(
        label=_('Active'),
        help_text=_('By default, the client meal status is Pending.'),
        required=False,
    )

    delivery_type = forms.ChoiceField(
        label=_('Type'),
        choices=DELIVERY_TYPE,
        required=True,
        widget=forms.Select(attrs={'class': 'ui dropdown'})
    )

    meals_schedule = forms.MultipleChoiceField(
        label=_('Schedule'),
        initial='Select days of week',
        choices=DAYS_OF_WEEK,
        widget=forms.SelectMultiple(attrs={'class': 'ui dropdown'}),
        required=False,
    )

    restrictions = forms.ModelMultipleChoiceField(
        label=_("Restrictions"),
        queryset=Restricted_item.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'ui dropdown search'})
    )

    food_preparation = forms.ModelMultipleChoiceField(
        label=_("Preparation"),
        required=False,
        queryset=Option.objects.filter(option_group='preparation'),
        widget=forms.SelectMultiple(attrs={'class': 'ui dropdown'}),
    )

    ingredient_to_avoid = forms.ModelMultipleChoiceField(
        label=_("Ingredient To Avoid"),
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui dropdown search'}
        )
    )

    dish_to_avoid = forms.ModelMultipleChoiceField(
        label=_("Dish(es) To Avoid"),
        queryset=Component.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui dropdown search'}
        )
    )


class MemberForm(forms.Form):

    member = forms.CharField(
        label=_("Member"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Member'),
            'class': 'prompt existing--member'
        }),
        required=False
    )

    firstname = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(attrs={
            'placeholder': _('First Name'),
            'class': 'firstname'
        }),
        required=False
    )

    lastname = forms.CharField(
        label=_("Last Name"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Last Name'),
            'class': 'lastname'
        }),
        required=False
    )

    def clean(self):
        cleaned_data = super(MemberForm, self).clean()

        """If the client pays for himself. """
        if cleaned_data.get('same_as_client') is True:
            return cleaned_data

        member = cleaned_data.get('member')
        firstname = cleaned_data.get('firstname')
        lastname = cleaned_data.get('lastname')

        if not member and (not firstname or not lastname):
            msg = _('This field is required unless you add a new member.')
            self.add_error('member', msg)
            msg = _(
                'This field is required unless you chose an existing member.'
            )
            self.add_error('firstname', msg)
            self.add_error('lastname', msg)

        if member:
            member_id = member.split(' ')[0].replace('[', '').replace(']', '')
            try:
                Member.objects.get(pk=member_id)
            except ObjectDoesNotExist:
                msg = _('Not a valid member, please chose an existing member.')
                self.add_error('member', msg)
        return cleaned_data


class ClientReferentInformation(MemberForm):

    work_information = forms.CharField(
        max_length=200,
        label=_('Work information'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Hotel-Dieu, St-Anne Hospital, ...')
        })
    )

    referral_reason = forms.CharField(
        label=_("Referral Reason"),
        widget=forms.Textarea(attrs={'rows': 4})
    )

    date = forms.DateField(label=_("Referral Date"))


class ClientPaymentInformation(MemberForm):

    facturation = forms.ChoiceField(
        label=_("Billing Type"),
        choices=RATE_TYPE,
        widget=forms.Select(attrs={'class': 'ui dropdown'})
    )

    same_as_client = forms.BooleanField(
        label=_("Same As Client"),
        required=False,
        help_text=_('If checked, the personal information \
            of the client will be used as billing information.'),
        widget=forms.CheckboxInput(
            attrs={}))

    billing_payment_type = forms.ChoiceField(
        label=_("Payment Type"),
        choices=PAYMENT_TYPE,
        widget=forms.Select(attrs={'class': 'ui dropdown'})
    )

    number = forms.IntegerField(label=_("Street Number"), required=False)

    apartment = forms.IntegerField(
        label=_("Apt #"),
        widget=forms.TextInput(attrs={'placeholder': _('Apt #')}),
        required=False
    )

    floor = forms.IntegerField(label=_("Floor"), required=False)

    street = forms.CharField(label=_("Street Name"), required=False)

    city = forms.CharField(label=_("City Name"), required=False)

    postal_code = forms.CharField(label=_("Postal Code"), required=False)

    def clean(self):
        cleaned_data = super(ClientPaymentInformation, self).clean()

        if cleaned_data.get('same_as_client') is True:
            return cleaned_data

        member = cleaned_data.get('member')
        if member:
            member_id = member.split(' ')[0].replace('[', '').replace(']', '')
            member_obj = Member.objects.get(pk=member_id)
            if not member_obj.address:
                msg = _('This member has not a valid address, '
                        'please add a valid address to this member, so it can '
                        'be used for the billing.')
                self.add_error('member', msg)
        else:
            msg = _("This field is required")
            fields = ['street', 'city', 'postal_code']
            for field in fields:
                field_data = cleaned_data.get(field)
                if not field_data:
                    self.add_error(field, msg)
        return cleaned_data


class ClientEmergencyContactInformation(MemberForm):

    contact_type = forms.ChoiceField(
        label=_("Contact Type"),
        choices=CONTACT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'ui dropdown'})
    )

    contact_value = forms.CharField(label=_("Contact"))


class ClientScheduledStatusForm(forms.ModelForm):

    class Meta:
        model = ClientScheduledStatus
        fields = [
            'client', 'status_from', 'status_to', 'reason', 'change_date'
        ]
        widgets = {
            'status_to': forms.Select(attrs={
                'class': 'ui status_to dropdown'
            }),
            'reason': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(ClientScheduledStatusForm, self).__init__(*args, **kwargs)
        self.fields['end_date'] = forms.DateField(required=False)


def load_initial_data(client):
    """
    Load initial for the given client.
    """
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
            client.client_referent.get().work_information
            if client.client_referent.count()
            else '',
        'referral_reason':
            client.client_referent.get().referral_reason
            if client.client_referent.count()
            else '',
        'date':
            client.client_referent.get().date
            if client.client_referent.count()
            else '',
        'member': client.id,
        'same_as_client': True,
        'facturation': '',
        'billing_payment_type': '',

    }
    return initial
