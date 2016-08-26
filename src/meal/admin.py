from django.contrib import admin
from meal.models import Component, Restricted_item
from meal.models import Ingredient, Component_ingredient
from meal.models import Incompatibility, Menu, Menu_component


class ComponentsInline(admin.TabularInline):
    model = Menu.components.through


class ComponentIngredientInline(admin.TabularInline):
    model = Component_ingredient


class MenuAdmin(admin.ModelAdmin):
    """Allows accessing menu components within the Menu admin."""
    inlines = [
        ComponentsInline
    ]


class ComponentAdmin(admin.ModelAdmin):
    """Allows accessing ingredients within the Component admin."""
    inlines = [
        ComponentIngredientInline
    ]


admin.site.register(Component, ComponentAdmin)
admin.site.register(Restricted_item)
admin.site.register(Ingredient)
admin.site.register(Incompatibility)
admin.site.register(Menu, MenuAdmin)
