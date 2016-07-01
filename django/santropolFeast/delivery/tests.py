from django.test import TestCase


class KitchenCountReportTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ground porc' clashing ingredient
        import dataload

    def test_clashing_ingredient(self):
        """An ingredient we know will clash must be in the page"""
        response = self.client.get('/delivery/kitchen_count/')
        self.assertTrue(b'Ground porc' in response.content)
