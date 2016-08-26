from django.contrib import admin
from billing.models import Billing


# Register your models here.
class OrdersInline(admin.TabularInline):
    model = Billing.orders.through


class BillingAdmin(admin.ModelAdmin):

    inlines = [
        OrdersInline,
    ]


admin.site.register(Billing, BillingAdmin)
