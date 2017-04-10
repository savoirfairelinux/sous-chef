from django.contrib import admin

from member.models import (
    Member, Client, Contact, Address,
    Referencing, Route, Option, EmergencyContact,
    DeliveryHistory
)


class IngredientsToAvoidInline(admin.TabularInline):
    model = Client.ingredients_to_avoid.through


class ComponentsToAvoidInline(admin.TabularInline):
    model = Client.components_to_avoid.through


class RestrictionsInline(admin.TabularInline):
    model = Client.restrictions.through


class OptionsInline(admin.TabularInline):
    model = Client.options.through


class ContactInline(admin.TabularInline):
    model = Contact


class ReferencingInline(admin.TabularInline):
    model = Referencing


class MemberAdmin(admin.ModelAdmin):
    search_fields = ['lastname', 'firstname']
    list_display = ('full_name', 'address', 'work_information', 'updated_at')
    inlines = [
        ContactInline
    ]

    def full_name(self, obj):
        return ("%s %s" % (obj.firstname, obj.lastname))
    full_name.short_description = 'Name'


class ClientAdmin(admin.ModelAdmin):
    search_fields = ['member__lastname', 'member__firstname']
    list_filter = ('status', 'route', 'delivery_type')
    list_display = (
        'member',
        'status',
        'language',
        'delivery_type',
        'gender',
        'route')
    inlines = [
        ReferencingInline,
        OptionsInline,
        RestrictionsInline,
        ComponentsToAvoidInline,
        IngredientsToAvoidInline
    ]


class ContactAdmin(admin.ModelAdmin):
    search_fields = ['member__lastname', 'member__firstname']
    list_display = ('member', 'type', 'value', )
    list_filter = ('type',)


class ReferencingAdmin(admin.ModelAdmin):
    search_fields = ['referent__lastname', 'referent__firstname']
    list_display = ('referent', 'client', 'referral_reason', 'date')


admin.site.register(Member, MemberAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Route)
admin.site.register(DeliveryHistory)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Address)
admin.site.register(Referencing, ReferencingAdmin)
admin.site.register(Option)
admin.site.register(EmergencyContact)
