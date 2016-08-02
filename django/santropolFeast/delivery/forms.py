from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple


class DateForm(forms.Form):
    date = forms.DateField(
        label=' ', widget=forms.SelectDateWidget)


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

    class Media:
        css = {'all': ('/static/admin/css/widgets.css', ), }
        js = ('/admin/jsi18n', )
