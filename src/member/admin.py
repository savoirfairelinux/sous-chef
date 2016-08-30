from django.contrib import admin
from member.models import (Member, Client, Contact, Address,
                           Referencing, Route, Option)

from meal.models import Ingredient


class IngredientsToAvoidInline(admin.TabularInline):
    model = Client.ingredients_to_avoid.through


class ComponentsToAvoidInline(admin.TabularInline):
    model = Client.components_to_avoid.through


class RestrictionsInline(admin.TabularInline):
    model = Client.restrictions.through


class OptionsInline(admin.TabularInline):
    model = Client.options.through


class ClientAdmin(admin.ModelAdmin):

    inlines = [
        OptionsInline,
        RestrictionsInline,
        ComponentsToAvoidInline,
        IngredientsToAvoidInline
    ]


admin.site.register(Member)
admin.site.register(Client, ClientAdmin)
admin.site.register(Route)
admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Referencing)
admin.site.register(Option)
