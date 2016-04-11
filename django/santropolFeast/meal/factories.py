# coding=utf-8

import factory
from meal.model import Meal, Ingredient, Allergy


class MealFactory(factory.DjangoModelFactory):
    class Meta:
        model = Meal

    nom = "Tomato Soupe"
    description = "A Simple Tomato Soupe"
    Ingredients = "Tomato"


class IngredientFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ingredient

    Ingredient = "Tomato"


class AllergyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Allergy

    nom = "Tomato"
    description = "A Simple Tomato"
    Ingredient = "Tomato"
