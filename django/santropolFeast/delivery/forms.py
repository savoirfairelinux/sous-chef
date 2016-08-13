from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models.functions import Lower

from meal.models import (
    COMPONENT_GROUP_CHOICES_MAIN_DISH, Component, Ingredient)


class DishIngredientsForm(forms.Form):
    maindish = forms.ModelChoiceField(
        label=_("Today's main dish:"),
        queryset=Component.objects.order_by(Lower('name')).filter(
            component_group=COMPONENT_GROUP_CHOICES_MAIN_DISH),
        widget=forms.Select,
    )

    ingredients = forms.ModelMultipleChoiceField(
        label=_('Select Ingredients:'),
        queryset=Ingredient.objects.order_by(Lower('name')).all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'ui fluid search dropdown'}),
        required=False,
    )
