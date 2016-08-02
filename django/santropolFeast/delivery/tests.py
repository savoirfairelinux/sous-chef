from django.test import TestCase
from dataload import insert_all


class KitchenCountReportTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ground porc' clashing ingredient
        insert_all()  # load fresh data into DB

    def test_clashing_ingredient(self):
        """An ingredient we know will clash must be in the page"""
        response = self.client.get('/delivery/kitchen_count/2016/05/21/')
        self.assertTrue(b'Ground porc' in response.content)


class ChooseDayMainDishIngredientsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ground porc' main dish ingredient
        #  for 2016-05-21
        # This data set includes 'Pepper' available ingredient
        insert_all()  # load fresh data into DB

    def test_known_ingredients(self):
        """Two ingredients we know must be in the page"""
        response = self.client.get('/delivery/meal/2016/05/21/')
        self.assertTrue(b'Ground porc' in response.content and
                        b'Pepper' in response.content)

    def test_no_main_dish_on_date(self):
        """No main dish on this date"""
        response = self.client.get('/delivery/meal/2016/05/01/')
        self.assertTrue(b'None for chosen date' in response.content)

    def test_change_date_with_dish(self):
        """Change main dish date."""
        response = self.client.get('/delivery/meal/')
        response = self.client.post(
            '/delivery/meal/',
            {'_change': 'Change',
             'date_year': '2016',
             'date_month': '5',
             'date_day': '21'})
        self.assertTrue('2016/05/21' in response.url)

    def test_date_with_dish_next(self):
        """From ingredient choice go to Kitchen Count Report."""
        response = self.client.get('/delivery/meal/2016/05/21/')
        response = self.client.post(
            '/delivery/meal/',
            {'_next': 'Next: Print Kitchen Count',
             'date': '2016-05-21',
             'dish': 'Ginger pork',
             'ingredients': ['Onion', 'Ground porc', 'soy sauce',
                             'green peppers', 'sesame seeds', 'celery']})
        self.assertTrue('/delivery/kitchen_count/2016/05/21' in response.url)

    def test_date_with_dish_back(self):
        """From ingredient choice go to Orders."""
        response = self.client.get('/delivery/meal/2016/05/21/')
        response = self.client.post('/delivery/meal/', {'_back': 'Back'})
        self.assertTrue('/delivery/order/' in response.url)

    def test_post_invalid_form(self):
        """Invalid form."""
        response = self.client.get('/delivery/meal/')
        response = self.client.post(
            '/delivery/meal/',
            {'_change': 'Change',
             'date_year': '2016',
             'date_month': '5',
             'date_day': '0'})
        self.assertTrue(b'Ingredients' in response.content)
