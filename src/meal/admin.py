from django.contrib import admin
from django.db.models.functions import Lower
from meal.models import (Component, Restricted_item,
                         Ingredient, Component_ingredient,
                         Incompatibility, Menu, Menu_component)


class ComponentsInline(admin.TabularInline):
    model = Menu.components.through


class ComponentIngredientInline(admin.TabularInline):
    model = Component_ingredient


class IncompatibilityInline(admin.TabularInline):
    model = Incompatibility


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
    list_display = ('name', 'component_group')
    search_fields = ['name', 'component_group']

    def get_ordering(self, request):
        return [Lower('name')]


class IngredientAdmin(admin.ModelAdmin):
    """Allows more control over the display of ingredients in the admin."""
    list_display = ('name', 'ingredient_group',)
    search_fields = ['name', 'ingredient_group']

    def get_ordering(self, request):
        return [Lower('name')]


class Restricted_itemAdmin(admin.ModelAdmin):
    """Allows accessing ingredients within the Restricted_item admin."""
    inlines = [
        IncompatibilityInline
    ]
    list_display = ('name', 'restricted_item_group',)
    search_fields = ['name', 'restricted_item_group']

    def get_ordering(self, request):
        return [Lower('name')]


admin.site.register(Component, ComponentAdmin)
admin.site.register(Restricted_item, Restricted_itemAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Menu, MenuAdmin)
