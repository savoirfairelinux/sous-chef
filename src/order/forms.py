from django import forms
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from extra_views import InlineFormSet

from member.models import Client

from meal.models import COMPONENT_GROUP_CHOICES, COMPONENT_GROUP_CHOICES_SIDES
from order.models import Order_item, SIZE_CHOICES, OrderStatusChange, \
    ORDER_ITEM_TYPE_CHOICES


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
        if 'delivery_dates' in kwargs:
            delivery_dates = kwargs['delivery_dates']
            del kwargs['delivery_dates']
        else:
            delivery_dates = None
        super(CreateOrdersBatchForm, self).__init__(*args, **kwargs)

        if delivery_dates:
            for d in delivery_dates:
                self.fields['size_{}'.format(d)] = forms.ChoiceField(
                    choices=SIZE_CHOICES,
                    widget=forms.Select(attrs={'class': ''}),
                    required=True
                )
                self.fields['delivery_{}'.format(d)] = forms.BooleanField(
                    required=False
                )
                self.fields['pickup_{}'.format(d)] = forms.BooleanField(
                    required=False
                )
                self.fields['visit_{}'.format(d)] = forms.BooleanField(
                    required=False
                )

                for meal, placeholder in COMPONENT_GROUP_CHOICES:
                    if meal is COMPONENT_GROUP_CHOICES_SIDES:
                        continue  # don't put "sides" on the form
                    self.fields[
                        '{}_{}_quantity'.format(meal, d)
                    ] = forms.IntegerField(
                        widget=forms.TextInput(
                            attrs={'placeholder': placeholder}
                        ),
                        required=True
                    )

    client = forms.ModelChoiceField(
        required=True,
        label=_('Client'),
        widget=BatchFormClientSelect(attrs={'class': 'ui search dropdown'}),
        queryset=Client.active.all().select_related(
            'member'
        ).only(
            'member__firstname',
            'member__lastname'
        )
    )

    delivery_dates = forms.CharField(
        required=True,
        label=_('Delivery dates'),
        max_length=200
    )

    override_dates = forms.CharField(
        required=False,
        label=_('Override dates'),
        max_length=200
    )

    is_submit = forms.IntegerField(
        required=True,
        label=_('Is form submit')
    )

    def clean_is_submit(self):
        is_submit = self.cleaned_data['is_submit']
        if is_submit is not 1:
            # prevents form submit and force a form refresh
            raise forms.ValidationError(
                _("This field must be 1 to submit the form.")
            )
        return is_submit


class OrderStatusChangeForm(forms.ModelForm):

    class Meta:
        model = OrderStatusChange
        fields = [
            'order', 'status_from', 'status_to', 'reason'
        ]
        widgets = {
            'status_to': forms.Select(
                attrs={'class': 'ui status_to dropdown disabled'}
            ),
            'reason': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super(OrderStatusChangeForm, self).clean()
        status_to = cleaned_data.get('status_to')
        reason = cleaned_data.get('reason')

        if status_to == 'N' and not reason:  # No Charge without reason
            self.add_error(
                'reason',
                forms.ValidationError(
                    _('A reason is required for No Charge order.'),
                    code='no_charge_reason_required'
                )
            )
        return cleaned_data
