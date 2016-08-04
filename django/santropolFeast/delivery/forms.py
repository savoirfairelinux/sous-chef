from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from meal.models import Ingredient, Component

class DateForm(forms.Form):
    date = forms.DateField(label=_(""))


class DayIngredientsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        try:
            self.choices = kwargs.pop('choices')
        except KeyError:
            raise KeyError("DayIngredientsForm missing kwarg : choices")
        super().__init__(*args, **kwargs)
        self.fields['ingredients'].choices = self.choices

    ingredients = forms.MultipleChoiceField(
        label=_('Ingredients'),
        widget=FilteredSelectMultiple(
            'Ingredients', is_stacked=False, attrs={'rows': '10'}),
        required=False,
    )

    ingredients_semantic = forms.ModelMultipleChoiceField(
        label=_("Ingredients Semantic"),
        queryset=Ingredient.objects.all(),
        initial=(Ingredient.objects.get(pk=1),),
        required=False,
        widget=forms.SelectMultiple(
            attrs={'class': 'ui fluid search dropdown'}
        )
    )

    date = forms.DateField(
        label=' ',
        widget=forms.HiddenInput,
        required=False,
    )

    dish = forms.CharField(
        label=' ',
        widget=forms.HiddenInput,
        required=False,
    )

    dish_semantic = forms.ModelChoiceField(
        label=_("Plat du jour:"),
        queryset=Component.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'class': 'ui search dropdown'}
        )
    )

    class Media:
        css = {'all': ('/static/admin/css/widgets.css', ), }
        js = ('/admin/jsi18n', )
