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
