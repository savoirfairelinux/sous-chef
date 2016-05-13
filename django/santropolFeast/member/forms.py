from django import forms
from member.models import Member


class ClientBasicInformation (forms.Form):

    firstname = forms.CharField(max_length=100, label="First Name")
    lastname = forms.CharField(max_length=100, label="Last Name")

    gender = forms.ChoiceField()

    # For test purpose only must be required for final version
    gender.required = False

    birthdate = forms.DateField()

    contact_type = forms.ChoiceField()
    # Remove the require = False
    contact_type.required = False
    contact_value = forms.CharField()

    alert = forms.CharField()


class ClientAddressInformation(forms.Form):

    number = forms.IntegerField(label="Street Number")

    apartment = forms.IntegerField(label="Apartment Number")
    apartment.required = False

    floor = forms.IntegerField(label="Floor")
    floor.required = False

    street = forms.CharField(max_length=100, label="Street Name")

    city = forms.CharField(max_length=50, label="City Name")

    postal_code = forms.CharField(max_length=6, label="Postal Code")


class ClientRestrictionsInformation(forms.Form):
    pass

    # Suppose to be many to many
    # client_restriction = forms


class ClientReferentInformation(forms.Form):

    firstname = forms.CharField(max_length=100, label="First Name")
    lastname = forms.CharField(max_length=100, label="Last Name")
    referral_reason = forms.CharField(label="Referral Reason")
    date = forms.DateField(label="Referral Date")


class ClientPaymentInformation(forms.Form):

    facturation = forms.ChoiceField(label="Billing Type")
    # Remove the require = False
    facturation.required = False

    firstname = forms.CharField(label="First Name")

    lastname = forms.CharField(label="Last Name")

    number = forms.IntegerField(label="Street Number")

    apartement = forms.CharField(label="Apartement Number")
    apartement.required = False

    floor = forms.IntegerField(label="Floor")
    floor.require = False

    street = forms.CharField(label="Street Name")

    city = forms.CharField(label="City Name")

    postal_code = forms.CharField(label="Postal Code")


class ClientEmergencyContactInformation(forms.Form):

    firstname = forms.CharField(label="First Name")

    lastname = forms.CharField(label="Last Name")

    contact_type = forms.ChoiceField(label="Contact Type")
    # Remove the require = False
    contact_type = False

    contact_value = forms.CharField(label="Contact")
