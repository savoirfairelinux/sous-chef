import re
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from member.formsfield import CAPhoneNumberExtField
from localflavor.ca.forms import (
    CAPhoneNumberField, CAPostalCodeField
)
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

    birthdate = forms.DateField(
        label=_("Birthday"),
        widget=forms.TextInput(attrs={'class': 'ui calendar'})
    )

    email = forms.EmailField(
        max_length=100,
        label='<i class="email icon"></i>',
        widget=forms.TextInput(attrs={'placeholder': _('Email')}),
        required=False,
    )

    home_phone = CAPhoneNumberExtField(
        label='Home',
        widget=forms.TextInput(attrs={'placeholder': _('Home phone')}),
        required=False,
    )

    cell_phone = CAPhoneNumberExtField(
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

    apartment = forms.CharField(
        label=_("Apt #"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Apt #'),
            'class': 'apartment'
        }),
        required=False
    )

    street = forms.CharField(
        max_length=100,
        label=_("Address information"),
        widget=forms.TextInput(attrs={
            'placeholder': _('7275 Rue Saint-Urbain'),
            'class': 'street name'
        })
    )

    city = forms.CharField(
        max_length=50,
        label=_("City"),
        widget=forms.TextInput(attrs={
            'placeholder': _('Montreal'),
            'class': 'city'
        })
    )

    postal_code = CAPostalCodeField(
        max_length=7,
        label=_("Postal Code"),
        widget=forms.TextInput(attrs={
            'placeholder': _('H2R 2Y5'),
            'class': 'postal code'
        })
    )

    latitude = forms.CharField(
        label=_('Latitude'),
        required=False,
        initial=0,
        widget=forms.TextInput(attrs={'class': 'latitude'})
    )

    longitude = forms.CharField(
        label=_('Longitude'),
        required=False,
        initial=0,
        widget=forms.TextInput(attrs={'class': 'longitude'})
    )

    distance = forms.CharField(
        label=_('Distance from Santropol'),
        required=False,
        initial=0,
        widget=forms.TextInput(attrs={'class': 'distance'})
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

        for day, translation in DAYS_OF_WEEK + (('default', _('Default')),):
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

    email = forms.EmailField(
        label='<i class="email icon"></i>',
        widget=forms.TextInput(attrs={'placeholder': _('Email')}),
        required=False,
    )

    work_phone = CAPhoneNumberExtField(
        label='Work',
        widget=forms.TextInput(attrs={'placeholder': _('Work phone')}),
        required=False,
    )

    cell_phone = CAPhoneNumberExtField(
        label='Cell',
        widget=forms.TextInput(attrs={'placeholder': _('Cellular')}),
        required=False,
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

    date = forms.DateField(
        label=_("Referral Date"),
        widget=forms.TextInput(attrs={'class': 'ui calendar'})
    )


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

    apartment = forms.CharField(
        label=_("Apt #"),
        widget=forms.TextInput(attrs={'placeholder': _('Apt #')}),
        required=False
    )

    floor = forms.IntegerField(label=_("Floor"), required=False)

    street = forms.CharField(label=_("Street Name"), required=False)

    city = forms.CharField(label=_("City Name"), required=False)

    postal_code = CAPostalCodeField(label=_("Postal Code"), required=False)

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
    # max_length come from models.Contact.value
    contact_value_kwargs = {'label': _("Contact"), 'max_length': 50}
    contact_value = forms.CharField(**contact_value_kwargs)

    relationship = forms.CharField(
        label=_("Relationship"),
        widget=forms.TextInput(
            attrs={'placeholder': _('Parent, friend, ...')}
        ),
        required=False
    )

    def clean_contact_value(self):
        try:
            contact_type = self.cleaned_data['contact_type']
            contact_value = self.cleaned_data['contact_value']
        except KeyError as ke:
            raise forms.ValidationError(ke.message)
        if contact_type == 'Email':
            field = forms.EmailField(**self.contact_value_kwargs)
        else:
            # CAPhoneNumberField is not a CharField (no max_length)
            field = CAPhoneNumberExtField()
        return field.clean(contact_value)


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
        self.fields['end_date'] = forms.DateField(
            required=False,
            widget=forms.TextInput(attrs={'class': 'ui calendar'})
        )
