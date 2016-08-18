import datetime

from django.test import TestCase

from meal.models import Component, Component_ingredient
from meal.models import Ingredient, Incompatibility
from meal.models import Menu, Menu_component, Restricted_item


class ComponentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        component = Component.objects.create(
            name='Coq au vin', component_group='main dish')

    def test_str_is_fullname(self):
        """Component's string representation is its name"""
        name = 'Coq au vin'
        component = Component.objects.get(name=name)
        self.assertEqual(name, str(component))


class Component_ingredientTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        component = Component.objects.create(
            name='Coq au vin', component_group='main dish')
        ingredient = Ingredient.objects.create(
            name='Green peas', ingredient_group='veggies and fruits')
        Component_ingredient.objects.create(component=component,
                                            ingredient=ingredient)

    def test_str_includes_all_names(self):
        """A Component_ingredient's string representation includes the name
        of the component and the name of the ingredient.
        """
        component = Component.objects.get(name='Coq au vin')
        ingredient = Ingredient.objects.get(name='Green peas')
        component_ingredient = Component_ingredient.objects.get(
            component=component, ingredient=ingredient)
        self.assertTrue(component.name in str(component_ingredient))
        self.assertTrue(ingredient.name in str(component_ingredient))


class IncompatibilityTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        restricted_item = Restricted_item.objects.create(
            name='pork', restricted_item_group='meat')
        ingredient = Ingredient.objects.create(
            name='ham', ingredient_group='meat')
        Incompatibility.objects.create(restricted_item=restricted_item,
                                       ingredient=ingredient)

    def test_str_includes_all_names(self):
        """Incompatibility's string representation includes the name
        of the restricted_item and the name of the ingredient.
        """
        restricted_item = Restricted_item.objects.get(name='pork')
        ingredient = Ingredient.objects.get(name='ham')
        incompatibility = Incompatibility.objects.get(
            restricted_item=restricted_item, ingredient=ingredient)
        self.assertTrue(restricted_item.name in str(incompatibility))
        self.assertTrue(ingredient.name in str(incompatibility))


class IngredientTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        ingredient = Ingredient.objects.create(
            name='Green peas', ingredient_group='veggies and fruits')

    def test_str_is_fullname(self):
        """Ingredient's string representation is its name"""
        name = 'Green peas'
        ingredient = Ingredient.objects.get(name=name)
        self.assertEqual(name, str(ingredient))


class MenuTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        menu = Menu.objects.create(date=datetime.date(2016, 5, 21))

    def test_str_is_fullname(self):
        """Menu's string representation includes date"""
        date = datetime.date(2016, 5, 21)
        menu = Menu.objects.get(date=date)
        self.assertTrue(str(date) in str(menu))


class Menu_componentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        menu = Menu.objects.create(date=datetime.date(2016, 5, 21))
        component = Component.objects.create(
            name='Coq au vin', component_group='main dish')
        Menu_component.objects.create(menu=menu, component=component)

    def test_str_includes_all_names(self):
        """A Menu_component's string representation includes the date
        of the menu and the name of the component.
        """
        date = datetime.date(2016, 5, 21)
        menu = Menu.objects.get(date=date)
        component = Component.objects.get(name='Coq au vin')
        menu_component = Menu_component.objects.get(
            menu=menu, component=component)
        self.assertTrue(str(date) in str(menu_component))
        self.assertTrue(component.name in str(menu_component))


class CreateMenuAndComponentsTestCase(TestCase):

    fixtures = ['meal_initial_data']

    def test_menu_new(self):
        number = Menu.create_menu_and_components(
            datetime.date(2016, 7, 15),
            ['Ginger pork',
             'Green Salad', 'Fruit Salad', 'Day s Dessert',
             'Day s Diabetic Dessert', 'Day s Pudding', 'Day s Compote'])
        self.assertEqual(number, 7)

    def test_menu_existed(self):
        Menu.create_menu_and_components(
            datetime.date(2016, 7, 15),
            ['Ginger pork',
             'Green Salad', 'Fruit Salad', 'Day s Dessert',
             'Day s Diabetic Dessert', 'Day s Pudding', 'Day s Compote'])
        number = Menu.create_menu_and_components(
            datetime.date(2016, 7, 15),
            ['Coq au vin',
             'Green Salad', 'Fruit Salad', 'Day s Dessert',
             'Day s Diabetic Dessert', 'Day s Pudding'])
        self.assertEqual(number, 6)

    def test_dish_does_not_exist_exception(self):
        with self.assertRaises(Exception) as cm:
            Menu.create_menu_and_components(
                datetime.date(2016, 7, 15),
                ['Chateaubriand Steak',
                 'Green Salad', 'Fruit Salad', 'Day s Dessert',
                 'Day s Diabetic Dessert', 'Day s Pudding', 'Day s Compote'])
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)

    def test_many_dishes_per_component_group_exception(self):
        with self.assertRaises(Exception) as cm:
            Menu.create_menu_and_components(
                datetime.date(2016, 7, 15),
                ['Ginger pork', 'Coq au vin',
                 'Green Salad', 'Fruit Salad', 'Day s Dessert',
                 'Day s Diabetic Dessert', 'Day s Pudding', 'Day s Compote'])
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)

    def test_no_main_dish_exception(self):
        with self.assertRaises(Exception) as cm:
            Menu.create_menu_and_components(
                datetime.date(2016, 7, 15),
                ['Green Salad', 'Fruit Salad', 'Day s Dessert',
                 'Day s Diabetic Dessert', 'Day s Pudding', 'Day s Compote'])
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)


class Restricted_itemTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        restricted_item = Restricted_item.objects.create(
            name='pork', restricted_item_group='meat')

    def test_str_is_fullname(self):
        """Restricted_Item's string representation is its name"""
        name = 'pork'
        restricted_item = Restricted_item.objects.get(name=name)
        self.assertEqual(name, str(restricted_item))
