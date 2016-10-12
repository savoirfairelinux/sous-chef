from django import forms
from django.utils.translation import ugettext_lazy as _
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
        widget=forms.Select(attrs={'class': 'ui search dropdown'}),
        queryset=Client.objects.all(),
    )

    delivery_dates = forms.CharField(
        required=True,
        label=_('Delivery dates'),
        max_length=200
    )
