from django.contrib import admin
from order.models import Order, OrderItem

admin.site.register(Order)
admin.site.register(OrderItem)