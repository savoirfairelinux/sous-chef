from django import forms
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from extra_views import InlineFormSet

from member.models import Client

from meal.models import COMPONENT_GROUP_CHOICES
from order.models import Order_item, SIZE_CHOICES


class CreateOrderItem(InlineFormSet):
    model = Order_item
    extra = 1
    fields = '__all__'


class UpdateOrderItem(CreateOrderItem):
    extra = 0


class BatchFormClientSelect(forms.Select):
    def render_option(self, selected_choices, option_value, option_label):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''

        data_url = reverse('member:client_meals_pref',
                           kwargs={'pk': option_value}) if option_value else ''
        return format_html('<option value="{}" data-url="{}"{}>{}</option>',
                           option_value,
                           data_url, selected_html, force_text(option_label))


class CreateOrdersBatchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(CreateOrdersBatchForm, self).__init__(*args, **kwargs)

        self.fields['size_{}'.format('default')] = forms.ChoiceField(
            choices=SIZE_CHOICES,
            widget=forms.Select(attrs={'class': 'ui dropdown'}),
            required=False
        )

        for meal, placeholder in COMPONENT_GROUP_CHOICES:
            self.fields['{}_{}_quantity'.format(meal, 'default')] = \
                forms.IntegerField(
                    widget=forms.TextInput(
                        attrs={'placeholder': placeholder}
                    ),
                    required=False
            )

    client = forms.ModelChoiceField(
        required=True,
        label=_('Client'),
        widget=BatchFormClientSelect(attrs={'class': 'ui search dropdown'}),
        queryset=Client.objects.all(),
    )

    delivery_dates = forms.CharField(
        required=True,
        label=_('Delivery dates'),
        max_length=200
    )
