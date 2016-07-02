# coding=utf-8

import factory
from meal.models import Ingredient


class IngredientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = "Tomato"

    @classmethod
    def __init__(self, **kwargs):
        name = kwargs.pop('name', None)
        ingredients = super(IngredientFactory, self).__init__(self, **kwargs)
        ingredients.save()
