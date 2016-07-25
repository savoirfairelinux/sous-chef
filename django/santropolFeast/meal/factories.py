# coding=utf-8

import factory
import random
from django.db import models
from faker import Factory as FakerFactory
from meal.models import (
    Ingredient, Component, Component_ingredient, Incompatibility,
    Restricted_item, INGREDIENT_GROUP_CHOICES, COMPONENT_GROUP_CHOICES,
    RESTRICTED_ITEM_GROUP_CHOICES, Menu, Menu_component
)

fake = FakerFactory.create()


class IngredientFactory(factory.DjangoModelFactory):

    class Meta:
        model = Ingredient

    name = fake.word()

    description = fake.sentence(nb_words=10, variable_nb_words=True)

    ingredient_group = factory.LazyAttribute(
        lambda x: random.choice(INGREDIENT_GROUP_CHOICES)[0]
    )


class ComponentFactory(factory.DjangoModelFactory):

    class Meta:
        model = Component

    name = fake.word()

    description = fake.sentence(nb_words=10, variable_nb_words=True)

    component_group = factory.LazyAttribute(
        lambda x: random.choice(COMPONENT_GROUP_CHOICES)[0]
    )


class ComponentIngredientFactory(factory.DjangoModelFactory):

    class Meta:
        model = Component_ingredient

    component = factory.SubFactory(ComponentFactory)

    ingredient = factory.SubFactory(IngredientFactory)


class RestrictedItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = Restricted_item

    name = fake.word()

    description = fake.sentence(nb_words=10, variable_nb_words=True)

    restricted_item_group = factory.LazyAttribute(
        lambda x: random.choice(RESTRICTED_ITEM_GROUP_CHOICES)[0]
    )


class IncompatibilityFactory(factory.DjangoModelFactory):

    class Meta:
        model = Incompatibility

    restricted_item = factory.SubFactory(RestrictedItemFactory)

    ingredient = factory.SubFactory(Ingredient)


class MenuFactory(factory.DjangoModelFactory):

    class Meta:
        model = Menu

    date = factory.LazyAttribute(lambda x: fake.date_time_between(
            start_date="-1y",
            end_date="+1y",
            tzinfo=None
        )
    )

    menu_component = factory.RelatedFactory(
        'meal.factories.MenuComponentFactory',
        'menu'
    )


class MenuComponentFactory(factory.DjangoModelFactory):

    class Meta:
        model = Menu_component

    menu = factory.SubFactory(MenuFactory)

    component = factory.SubFactory(ComponentFactory)
