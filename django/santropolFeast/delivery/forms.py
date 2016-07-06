from django import forms


class dateForm(forms.Form):
    date = forms.DateField(required=False)
