from django import forms
from django.forms import ModelForm
from order.models import Order_item


class CreateOrderItemForm(ModelForm):
    class Meta:
        model = Order_item
        fields = [
            'component', 'total_quantity', 'free_quantity', 'price',
            'billable_flag', 'size', 'remark'
        ]
