from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from member.models import Member, Client, Contact, Address


class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'member',
        'status',
    )

    fieldsets = [
        (
            _('Identification'), {
                'fields': (
                    ('member', 'status',),
                    'emergency_contact',
                )
            },
        ),
        (
            _('Billing'), {
                'fields': (
                    ('billing_address', 'billing_type',),
                )
            },
        ),
        (
            _('Meals'), {
                'fields': (
                    ('restrictions', 'allergies',),
                )
            },
        ),
        (
            _('Alerts'), {
                'fields': (
                    'alert',
                )
            }
        )
    ]


admin.site.register(Member)
admin.site.register(Client, ClientAdmin)
admin.site.register(Contact)
admin.site.register(Address)
