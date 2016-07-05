from django import forms
from django.utils.translation import ugettext_lazy as _
from member.models import (
    Client, RATE_TYPE, CONTACT_TYPE_CHOICES,
    GENDER_CHOICES, PAYMENT_TYPE, DELIVERY_TYPE,
    DAYS_OF_WEEK
)
from meal.models import Ingredient
from order.models import SIZE_CHOICES


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

    language = forms.ChoiceField(
        choices=Client.LANGUAGES,
        label=_("Preferred language"),
        widget=forms.Select(
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
    size_monday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_monday.required = False

    main_dish_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_monday_quantity.required = False

    dessert_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_monday_quantity.required = False

    diabetic_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_monday_quantity.required = False

    fruit_salad_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_monday_quantity.required = False

    green_salad_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_monday_quantity.required = False

    pudding_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Pudding')}
    ))
    pudding_monday_quantity.required = False

    compote_monday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_monday_quantity.required = False

    size_tuesday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_tuesday.required = False

    main_dish_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_tuesday_quantity.required = False

    dessert_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_tuesday_quantity.required = False

    diabetic_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_tuesday_quantity.required = False

    fruit_salad_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_tuesday_quantity.required = False

    green_salad_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_tuesday_quantity.required = False

    pudding_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Pudding')}
    ))
    pudding_tuesday_quantity.required = False

    compote_tuesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_tuesday_quantity.required = False

    size_wednesday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_wednesday.required = False

    main_dish_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_wednesday_quantity.required = False

    dessert_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_wednesday_quantity.required = False

    diabetic_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_wednesday_quantity.required = False

    fruit_salad_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_wednesday_quantity.required = False

    green_salad_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_wednesday_quantity.required = False

    pudding_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    pudding_wednesday_quantity.required = False

    compote_wednesday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_wednesday_quantity.required = False

    size_thursday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_thursday.required = False

    main_dish_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_thursday_quantity.required = False

    dessert_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_thursday_quantity.required = False

    diabetic_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_thursday_quantity.required = False

    fruit_salad_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_thursday_quantity.required = False

    green_salad_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_thursday_quantity.required = False

    pudding_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Pudding')}
    ))
    pudding_thursday_quantity.required = False

    compote_thursday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_thursday_quantity.required = False

    size_friday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_friday.required = False

    main_dish_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_friday_quantity.required = False

    dessert_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_friday_quantity.required = False

    diabetic_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_friday_quantity.required = False

    fruit_salad_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_friday_quantity.required = False

    green_salad_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_friday_quantity.required = False

    pudding_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Pudding')}
    ))
    pudding_friday_quantity.required = False

    compote_friday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_friday_quantity.required = False

    size_saturday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_saturday.required = False

    main_dish_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_saturday_quantity.required = False

    dessert_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_saturday_quantity.required = False

    diabetic_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_saturday_quantity.required = False

    fruit_salad_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_saturday_quantity.required = False

    green_salad_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_saturday_quantity.required = False

    pudding_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Pudding')}
    ))
    pudding_saturday_quantity.required = False

    compote_saturday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_saturday_quantity.required = False

    size_sunday = forms.ChoiceField(
        choices=SIZE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'ui dropdown'}
        )
    )
    size_sunday.required = False

    main_dish_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Main Dish')}
    ))
    main_dish_sunday_quantity.required = False

    dessert_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Dessert')}
    ))
    dessert_sunday_quantity.required = False

    diabetic_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Diabetic Dessert')}
    ))
    diabetic_sunday_quantity.required = False

    fruit_salad_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Fruit Salad')}
    ))
    fruit_salad_sunday_quantity.required = False

    green_salad_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Green Salad')}
    ))
    green_salad_sunday_quantity.required = False

    pudding_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Pudding')}
    ))
    pudding_sunday_quantity.required = False

    compote_sunday_quantity = forms.IntegerField(widget=forms.TextInput(
        attrs={'placeholder': _('Compote')}
    ))
    compote_sunday_quantity.required = False

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

    food_preparation = forms.ModelMultipleChoiceField(
        label=_("Preparation"),
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui dropdown search'}
        )
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
        label=_("Dish To Avoid"),
        queryset=Ingredient.objects.all(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui dropdown search'}
        )
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
