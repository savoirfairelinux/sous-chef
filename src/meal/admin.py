from django.contrib import admin
from django.db.models.functions import Lower
from meal.models import (Component, Restricted_item,
                         Ingredient, Component_ingredient,
                         Incompatibility, Menu, Menu_component,
                         COMPONENT_GROUP_CHOICES,
                         INGREDIENT_GROUP_CHOICES,
                         RESTRICTED_ITEM_GROUP_CHOICES)


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
    search_fields = ('name',)

    def get_ordering(self, request):
        return [Lower('name')]

    def get_search_results(self, request, queryset, search_term):
        # search for group choices in their display value instead of DB value
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term)
        search_list = [choice[0] for
                       choice in COMPONENT_GROUP_CHOICES
                       if search_term in choice[1]]
        if search_list:
            queryset |= self.model.objects.filter(
                component_group__in=search_list)
        return queryset, use_distinct


class IngredientAdmin(admin.ModelAdmin):
    """Allows more control over the display of ingredients in the admin."""
    list_display = ('name', 'ingredient_group',)
    search_fields = ('name',)

    def get_ordering(self, request):
        return [Lower('name')]

    def get_search_results(self, request, queryset, search_term):
        # search for group choices in their display value instead of DB value
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term)
        search_list = [choice[0] for
                       choice in INGREDIENT_GROUP_CHOICES
                       if search_term in choice[1]]
        if search_list:
            queryset |= self.model.objects.filter(
                ingredient_group__in=search_list)
        return queryset, use_distinct


class Restricted_itemAdmin(admin.ModelAdmin):
    """Allows accessing ingredients within the Restricted_item admin."""
    inlines = [
        IncompatibilityInline
    ]
    list_display = ('name', 'restricted_item_group',)
    search_fields = ('name',)

    def get_ordering(self, request):
        return [Lower('name')]

    def get_search_results(self, request, queryset, search_term):
        # search for group choices in their display value instead of DB value
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term)
        search_list = [choice[0] for
                       choice in RESTRICTED_ITEM_GROUP_CHOICES
                       if search_term in choice[1]]
        if search_list:
            queryset |= self.model.objects.filter(
                restricted_item_group__in=search_list)
        return queryset, use_distinct

admin.site.register(Component, ComponentAdmin)
admin.site.register(Restricted_item, Restricted_itemAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Menu, MenuAdmin)
