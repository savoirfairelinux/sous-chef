from django import forms
from django.utils.translation import ugettext_lazy as _
from member.models import (
    Client, RATE_TYPE, CONTACT_TYPE_CHOICES,
    GENDER_CHOICES, PAYMENT_TYPE, DELIVERY_TYPE,
    DAYS_OF_WEEK
)
from meal.models import Ingredient


class ClientBasicInformation (forms.Form):

    firstname = forms.CharField(max_length=100, label=_("First Name"),
                                widget=forms.TextInput(
                                    attrs={'placeholder': _('First name')}))

    lastname = forms.CharField(max_length=100, label=_("Last Name"),
                               widget=forms.TextInput(
        attrs={'placeholder': _('Last name')}))

    gender = forms.ChoiceField(choices=GENDER_CHOICES,
                               widget=forms.Select(
                                   attrs={'class': 'ui dropdown'}))

    languages = forms.TypedMultipleChoiceField(
        choices=Client.LANGUAGES,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'ui dropdown'}))

    birthdate = forms.DateField(label=_("Birthday"))

    contact_type = forms.ChoiceField(choices=CONTACT_TYPE_CHOICES,
                                     label=_("Contact Type"),
                                     widget=forms.Select(
                                         attrs={'class': 'ui dropdown'}))

    contact_value = forms.CharField(label=_("Contact information"))

    alert = forms.CharField(label=_("Alert"),
                            required=False,
                            widget=forms.Textarea(
        attrs={'rows': 2, 'placeholder': _('Your message here ...')}
    ))


class ClientAddressInformation(forms.Form):

    number = forms.IntegerField(label=_("Street Number"),
                                widget=forms.TextInput(
                                    attrs={'placeholder': _('#')}))
    number.required = False

    apartment = forms.IntegerField(label=_("Apt #"),
                                   widget=forms.TextInput(
        attrs={'placeholder': _('Apt #')}))
    apartment.required = False

    floor = forms.IntegerField(label=_("Floor"))
    floor.required = False

    street = forms.CharField(max_length=100, label=_("Street Name"),
                             widget=forms.TextInput(
        attrs={'placeholder': _('Street Address')}))

    city = forms.CharField(max_length=50, label=_("City"),
                           widget=forms.TextInput(
        attrs={'placeholder': _('Montreal')}))

    postal_code = forms.CharField(max_length=6, label=_("Postal Code"),
                                  widget=forms.TextInput(
        attrs={'placeholder': _('H2R 2Y5')}))


class ClientRestrictionsInformation(forms.Form):

    status = forms.BooleanField(
        label=_('Active'),
        help_text=_('By default, the client meal status is Pending.'),
        required=False,
    )

    delivery_type = forms.ChoiceField(
        label=_('Type'),
        choices=DELIVERY_TYPE,
        required=True,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )

    delivery_schedule = forms.MultipleChoiceField(
        label=_('Schedule'),
        initial='Select days of week',
        choices=DAYS_OF_WEEK,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui dropdown'}
        ),
        required=False,
    )

    restrictions = forms.ModelMultipleChoiceField(
        label=_("Restrictions"),
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui dropdown search'})
    )


class ClientReferentInformation(forms.Form):

    firstname = forms.CharField(max_length=100, label=_("First Name"),
                                widget=forms.TextInput(
                                    attrs={'placeholder': _('First Name')}))
    lastname = forms.CharField(max_length=100, label=_("Last Name"),
                               widget=forms.TextInput(
        attrs={'placeholder': _('Last Name')}))

    work_information = forms.CharField(
        max_length=200,
        label=_('Work information'),
        widget=forms.TextInput(
            attrs={
                'placeholder': _('Hotel-Dieu, St-Anne Hospital, CLSC, ...')}))

    referral_reason = forms.CharField(label=_("Referral Reason"),
                                      widget=forms.Textarea(
        attrs={'rows': 4}
    ))
    date = forms.DateField(label=_("Referral Date"))


class ClientPaymentInformation(forms.Form):

    facturation = forms.ChoiceField(label=_("Billing Type"),
                                    choices=RATE_TYPE,
                                    widget=forms.Select(
        attrs={'class': 'ui dropdown'})
    )

    billing_payment_type = forms.ChoiceField(label=_("Payment Type"),
                                             choices=PAYMENT_TYPE,
                                             widget=forms.Select(
        attrs={'class': 'ui dropdown'})
    )

    firstname = forms.CharField(label=_("First Name"), widget=forms.TextInput(
        attrs={'placeholder': _('First Name')}))

    lastname = forms.CharField(label=_("Last Name"), widget=forms.TextInput(
        attrs={'placeholder': _('Last Name')}))

    number = forms.IntegerField(label=_("Street Number"))
    number.required = False

    apartment = forms.IntegerField(label=_("Apt #"),
                                   widget=forms.TextInput(
        attrs={'placeholder': _('Apt #')}))
    apartment.required = False

    floor = forms.IntegerField(label=_("Floor"))
    floor.required = False

    street = forms.CharField(label=_("Street Name"))

    city = forms.CharField(label=_("City Name"))

    postal_code = forms.CharField(label=_("Postal Code"))


class ClientEmergencyContactInformation(forms.Form):

    firstname = forms.CharField(label=_("First Name"), widget=forms.TextInput(
        attrs={'placeholder': _('First Name')}))

    lastname = forms.CharField(label=_("Last Name"), widget=forms.TextInput(
        attrs={'placeholder': _('Last Name')}))

    contact_type = forms.ChoiceField(label=_("Contact Type"),
                                     choices=CONTACT_TYPE_CHOICES,
                                     widget=forms.Select(
                                         attrs={'class': 'ui dropdown'}))

    contact_value = forms.CharField(label=_("Contact"))
