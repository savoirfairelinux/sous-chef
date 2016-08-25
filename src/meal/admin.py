from django.contrib import admin
from meal.models import Component, Restricted_item
from meal.models import Ingredient, Component_ingredient
from meal.models import Incompatibility, Menu, Menu_component


class ComponentsInline(admin.TabularInline):
    model = Menu.components.through


class MenuAdmin(admin.ModelAdmin):

    inlines = [
        ComponentsInline
    ]


admin.site.register(Component)
admin.site.register(Restricted_item)
admin.site.register(Ingredient)
admin.site.register(Component_ingredient)
admin.site.register(Incompatibility)
admin.site.register(Menu, MenuAdmin)
