from django.contrib import admin
from meal.models import Component, Restricted_item, Ingredient

admin.site.register(Component)
admin.site.register(Restricted_item)
admin.site.register(Ingredient)
