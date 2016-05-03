from django import forms
from django.utils.translation import ugettext_lazy as _
from member.models import *
from meal.models import *


class ClientBasicInformation (forms.Form):

    firstname = forms.CharField(max_length=100, label=_("First Name"))
    lastname = forms.CharField(max_length=100, label=_("Last Name"))

    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    birthdate = forms.DateField(label=_("Birthday"))

    contact_type = forms.ChoiceField(choices=CONTACT_TYPE_CHOICES,
                                     label=_("Contact Type"))

    contact_value = forms.CharField(label=_("Contact information"))

    alert = forms.CharField(label=_("Alert"))


class ClientAddressInformation(forms.Form):

    number = forms.IntegerField(label=_("Street Number"))

    apartment = forms.IntegerField(label=_("Apartment Number"))
    apartment.required = False

    floor = forms.IntegerField(label=_("Floor"))
    floor.required = False

    street = forms.CharField(max_length=100, label=_("Street Name"))

    city = forms.CharField(max_length=50, label=_("City Name"))

    postal_code = forms.CharField(max_length=6, label=_("Postal Code"))


class ClientRestrictionsInformation(forms.Form):
    allergy = forms.TypedMultipleChoiceField(
        label=_("Allergy"),
        choices=ALLERGY_CHOICES
        )
    restrictions = forms.TypedMultipleChoiceField(
        label=_("Dietary Restrictions"),
        choices=ALLERGY_CHOICES
        )


class ClientReferentInformation(forms.Form):

    firstname = forms.CharField(max_length=100, label=_("First Name"))
    lastname = forms.CharField(max_length=100, label=_("Last Name"))
    referral_reason = forms.CharField(label=_("Referral Reason"))
    date = forms.DateField(label=_("Referral Date"))


class ClientPaymentInformation(forms.Form):

    facturation = forms.ChoiceField(label=_("Billing Type"),
                                    choices=FACTURATION_TYPE
                                    )

    Firstname = forms.CharField(label=_("First Name"))

    lastname = forms.CharField(label=_("Last Name"))

    number = forms.IntegerField(label=_("Street Number"))

    apartement = forms.CharField(label=_("Apartement Number"))
    apartement.required = False

    floor = forms.IntegerField(label=_("Floor"))
    floor.required = False

    street = forms.CharField(label=_("Street Name"))

    city = forms.CharField(label=_("City Name"))

    postal_code = forms.CharField(label=_("Postal Code"))


class ClientEmergencyContactInformation(forms.Form):

    firstname = forms.CharField(label=_("First Name"))

    lastname = forms.CharField(label=_("Last Name"))

    contact_type = forms.ChoiceField(label=_("Contact Type"),
                                     choices=CONTACT_TYPE_CHOICES)

    contact_value = forms.CharField(label=_("Contact"))
