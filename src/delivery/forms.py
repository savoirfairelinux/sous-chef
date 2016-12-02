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
        widget=forms.Select(attrs={'class': 'ui dropdown maindish'}),
    )

    ingredients = forms.ModelMultipleChoiceField(
        label=_('Select main dish ingredients:'),
        queryset=Ingredient.objects.order_by(Lower('name')).all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'ui fluid search dropdown'}),
        required=False,
    )

    sides_ingredients = forms.ModelMultipleChoiceField(
        label=_('Select sides ingredients:'),
        queryset=Ingredient.objects.order_by(Lower('name')).all(),
        widget=forms.SelectMultiple(
            attrs={'class': 'ui fluid search dropdown'}),
        required=False,
    )

    def clean_sides_ingredients(self):
        data = self.cleaned_data['sides_ingredients']
        if not data:
            raise forms.ValidationError(
                _("Please choose some Sides ingredients"))
        return data
