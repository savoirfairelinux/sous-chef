from django.contrib import admin
from billing.models import Billing, OrderBilling

# Register your models here.
admin.site.register(Billing)
admin.site.register(OrderBilling)
