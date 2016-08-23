import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse_lazy

from meal.models import Menu, Component, Component_ingredient, Ingredient
from order.models import Order
from member.models import Client


class KitchenCountReportTestCase(TestCase):

    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ground porc' clashing ingredient
        Menu.create_menu_and_components(
            datetime.date(2016, 5, 21),
            ['Ginger pork',
             'Green Salad', 'Fruit Salad',
             'Day s Dessert', 'Day s Diabetic Dessert',
             'Day s Pudding', 'Day s Compote'])

    def test_clashing_ingredient(self):
        """An ingredient we know will clash must be in the page"""
        response = self.client.get('/delivery/kitchen_count/2016/05/21/')
        self.assertTrue(b'Ground porc' in response.content)

    def test_no_components(self):
        """No orders on this day therefore no component summary"""
        response = self.client.get('/delivery/kitchen_count/2015/05/21/')
        self.assertTrue(b'SUBTOTAL' not in response.content)


class ChooseDayMainDishIngredientsTestCase(TestCase):

    fixtures = ['initial_data']

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ginger pork' main dish
        # This data set includes 'Coq au vin' main dish
        # This data set includes 'Ground porc' main dish ingredient
        # This data set includes 'Pepper' available ingredient
        # create orders for today
        clients = Client.active.all()
        Order.create_orders_on_defaults(
            datetime.date.today(),
            datetime.date.today(),
            clients)

    def test_known_ingredients(self):
        """Two ingredients we know must be in the page"""
        response = self.client.get(reverse_lazy('delivery:meal'))
        self.assertTrue(b'Ground porc' in response.content and
                        b'Pepper' in response.content)

    def test_date_with_dish_next(self):
        """From ingredient choice go to Kitchen Count Report."""
        response = self.client.get(reverse_lazy('delivery:meal'))
        maindish = Component.objects.get(name='Ginger pork')
        cis = Component_ingredient.objects.filter(
            date=None, component=maindish)
        ing_ids = [ci.ingredient.id for ci in cis]
        req = {}
        req['_next'] = 'Next: Print Kitchen Count'
        req['maindish'] = str(maindish.id)
        req['ingredients'] = ing_ids
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        response = self.client.get(reverse_lazy('delivery:kitchen_count'))
        self.assertTrue(b'Ginger pork' in response.content)

    def test_remember_day_ingredients(self):
        """After Kitchen Count Report we remember chosen ingredients."""
        response = self.client.get(reverse_lazy('delivery:meal'))
        maindish = Component.objects.get(name='Ginger pork')
        cis = Component_ingredient.objects.filter(
            date=None, component=maindish)
        ing_ids = [ci.ingredient.id for ci in cis]
        req = {}
        req['_next'] = 'Next: Print Kitchen Count'
        req['maindish'] = str(maindish.id)
        req['ingredients'] = ing_ids
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        response = self.client.get(reverse_lazy('delivery:kitchen_count'))
        self.assertTrue(b'Ginger pork' in response.content)
        response = self.client.get(reverse_lazy('delivery:meal'))
        self.assertTrue(b'Ginger pork' in response.content)

    def test_restore_dish_recipe(self):
        """Restore dish ingredients to those of recipe."""
        # dish : Ginger pork with added Pepper
        response = self.client.get(reverse_lazy('delivery:meal'))
        maindish = Component.objects.get(name='Ginger pork')
        cis = Component_ingredient.objects.filter(
            date=None, component=maindish)
        ing_ids = [ci.ingredient.id for ci in cis]
        ing_ids.append(Ingredient.objects.get(name='Pepper').id)
        req = {}
        req['_next'] = 'Next: Print Kitchen Count'
        req['maindish'] = str(maindish.id)
        req['ingredients'] = ing_ids
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        # restore recipe
        req = {}
        req['_restore'] = 'Restore recipe'
        req['maindish'] = str(maindish.id)
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        # check that we have Ginger pork with no Pepper in Kitchen count
        response = self.client.get(reverse_lazy('delivery:kitchen_count'))
        self.assertTrue(b'Ginger pork' in response.content and
                        b'Pepper' not in response.content)

    def test_change_main_dish(self):
        """Change dish then go directly to Kitchen Count Report."""
        maindish = Component.objects.get(name='Coq au vin')

        response = self.client.get(
            reverse_lazy('delivery:meal_id', args=[maindish.id]))
        req = {}
        req['_next'] = 'Next: Print Kitchen Count'
        req['maindish'] = str(maindish.id)
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        response = self.client.get(reverse_lazy('delivery:kitchen_count'))
        self.assertTrue(b'Coq au vin' in response.content)

    def test_post_invalid_form(self):
        """Invalid form."""
        response = self.client.get(reverse_lazy('delivery:meal'))
        req = {}
        req['_restore'] = 'Next: Print Kitchen Count'
        req['maindish'] = 'wrong'
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        self.assertTrue(b'Select a valid choice.' in response.content)
