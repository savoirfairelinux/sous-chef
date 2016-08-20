from django.db.models.functions import Lower
from django.contrib import admin
from meal.models import Component, Restricted_item
from meal.models import Ingredient, Component_ingredient
from meal.models import Incompatibility, Menu, Menu_component


# Component model and its relationships
#
class ComponentIngredientInline(admin.TabularInline):
    model = Component_ingredient
    fields = ('ingredient', 'ingredient_group',)
    readonly_fields = ('ingredient_group',)
    extra = 1

    def get_queryset(self, request):
        return (Component_ingredient.objects.
                filter(date=None).
                order_by(Lower('ingredient__ingredient_group'),
                         Lower('ingredient__name')))

    def ingredient_group(self, instance):
        return instance.ingredient.ingredient_group


class ComponentAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'description',
        'component_group',
    )

    inlines = (
        ComponentIngredientInline,
    )

admin.site.register(Component, ComponentAdmin)
# END Component


# Restricted_item model and its relationships
#
class IncompatibilityInline(admin.TabularInline):
    model = Incompatibility
    fields = ('ingredient', 'ingredient_group',)
    readonly_fields = ('ingredient_group',)
    extra = 1

    def get_queryset(self, request):
        return (Incompatibility.objects.
                order_by(Lower('ingredient__ingredient_group'),
                         Lower('ingredient__name')))

    def ingredient_group(self, instance):
        return instance.ingredient.ingredient_group


class RestrictedItemAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'description',
        'restricted_item_group',
    )

    inlines = (
        IncompatibilityInline,
    )

admin.site.register(Restricted_item, RestrictedItemAdmin)
# END Restricted_item

admin.site.register(Ingredient)
admin.site.register(Component_ingredient)
admin.site.register(Incompatibility)
admin.site.register(Menu)
admin.site.register(Menu_component)
