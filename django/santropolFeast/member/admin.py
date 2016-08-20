from django.contrib import admin
from member.models import (Member, Client, Contact, Address,
                           Referencing, Route, Client_avoid_component,
                           Client_avoid_ingredient, Option,
                           Client_option, Restriction)


admin.site.register(Member)


# Client model and its relationships
#
class RestrictionInline(admin.TabularInline):
    model = Restriction
    extra = 1


class ClientAvoidIngredientInline(admin.TabularInline):
    model = Client_avoid_ingredient
    extra = 1


class ClientAvoidComponentInline(admin.TabularInline):
    model = Client_avoid_component
    extra = 1


class ReferencingInline(admin.StackedInline):
    model = Referencing
    fields = ('referent', 'date', 'referral_reason', 'work_information')
    extra = 0


class ClientOptionInline(admin.TabularInline):
    fields = ('option', 'option_group', 'value',)
    readonly_fields = ('option_group',)
    model = Client_option
    extra = 1

    def option_group(self, instance):
        return instance.option.option_group


class ClientAdmin(admin.ModelAdmin):
    fields = (
        'member',
        'address_details',
        'gender',
        'language',
        'delivery_type',
        'birthdate',
        'billing_member',
        'billing_payment_type',
        'rate_type',
        'emergency_contact',
        'emergency_contact_relationship',
        'status',
        'alert',
        'route',
        'meal_default_week',
        'delivery_note',
    )
    readonly_fields = ('address_details',)

    inlines = (
        ClientOptionInline,
        ClientAvoidIngredientInline,
        ClientAvoidComponentInline,
        RestrictionInline,
        ReferencingInline,
    )

    def address_details(self, instance):
        address = instance.member.address
        return (
            '{} '.format(address.number) +
            '{}, '.format(address.street) +
            ('Apt {}, '.format(address.apartment) if address.apartment
             else '') +
            ('{} floor, '.format(address.floor) if address.floor
             else '') +
            '{} '.format(address.city) +
            '{}'.format(address.postal_code)
        )

admin.site.register(Client, ClientAdmin)
# END Client

admin.site.register(Route)
admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Referencing)
admin.site.register(Client_avoid_component)
admin.site.register(Client_avoid_ingredient)
admin.site.register(Option)
admin.site.register(Client_option)
admin.site.register(Restriction)
