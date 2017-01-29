from django.contrib import admin
from order.models import Order, Order_item, OrderStatusChange


def make_delivered(modeladmin, request, queryset):
    queryset.update(status='D')
make_delivered.short_description = "Mark selected orders as delivered"


class OrderItemInline(admin.TabularInline):
    model = Order_item


class OrderItemAdmin(admin.ModelAdmin):
    search_fields = ['order__id']
    list_display = (
        'order',
        'order_item_type',
        'component_group',
        'total_quantity',
        'billable_flag',
        'price',
    )


class OrderAdmin(admin.ModelAdmin):
    search_fields = ['client__member__lastname', 'client__member__firstname']
    list_filter = ('status', 'delivery_date')
    list_display = (
        'id',
        'client',
        'status',
        'price',
        'delivery_date',
        'creation_date',
    )
    actions = [make_delivered]
    inlines = [
        OrderItemInline
    ]

admin.site.register(Order, OrderAdmin)
admin.site.register(Order_item, OrderItemAdmin)
admin.site.register(OrderStatusChange)
