from extra_views import InlineFormSet

from order.models import Order_item


class CreateOrderItem(InlineFormSet):
    model = Order_item
    extra = 1
    fields = '__all__'


class UpdateOrderItem(CreateOrderItem):
    extra = 0
