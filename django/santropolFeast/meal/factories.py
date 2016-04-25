# coding=utf-8

import factory
from meal.model import Meal, Ingredient, Allergy


class MealFactory(factory.DjangoModelFactory):
    class Meta:
        model = Meal

    name = "Tomato Soupe"
    description = "A Simple Tomato Soupe"
    size = "R"

    @classmethod
    def __init__(self, **kwargs):
        name = kwargs.pop("name", None)

        meal = super(MealFactory, self).__init__(self, **kwargs)
        meal.save()


class IngredientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = "Tomato"

    @classmethod
    def __init__(self, **kwargs):
        name = kwargs.pop('name', None)
        ingredients = super(IngredientFactory, self).__init__(self, **kwargs)
        ingredients.save()


class AllergyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Allergy

    name = "Tomato"
    description = "A Simple Tomato"

    @classmethod
    def __init__(self, **kwargs):
        name = kwargs.pop("name", None)
        allergy = super(AllergyFactory, self).__init__(self, **kwargs)
        allergy.save()
