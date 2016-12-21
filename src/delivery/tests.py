import datetime
import json
import importlib

from django.db.models import Q
from django.test import RequestFactory
from django.test import TestCase
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils import timezone as tz

from meal.models import Menu, Component, Component_ingredient, Ingredient
from order.models import Order
from member.models import Client, Member, Route
from sous_chef.tests import TestMixin as SousChefTestMixin

from .filters import KitchenCountOrderFilter


class KitchenCountReportTestCase(SousChefTestMixin, TestCase):

    fixtures = ['sample_data']

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ground porc' clashing ingredient
        Menu.create_menu_and_components(
            datetime.date(2016, 5, 21),
            ['Ginger pork',
             'Green Salad', 'Fruit Salad',
             'Day s Dessert', 'Day s Diabetic Dessert',
             'Day s Pudding', 'Day s Compote'])

    def setUp(self):
        self.force_login()

    def test_clashing_ingredient(self):
        """An ingredient we know will clash must be in the page"""
        self.today = datetime.date.today()
        # create orders today
        clients = Client.active.all()
        numorders = Order.objects.auto_create_orders(
            self.today, clients)
        # main dish and its ingredients today
        main_dishes = Component.objects.filter(name='Ginger pork')
        main_dish = main_dishes[0]
        dish_ingredients = Component.get_recipe_ingredients(
            main_dish.id)
        for ing in dish_ingredients:
            ci = Component_ingredient(
                component=main_dish,
                ingredient=ing,
                date=self.today)
            ci.save()
        # menu today
        Menu.create_menu_and_components(
            self.today,
            ['Ginger pork',
             'Green Salad', 'Fruit Salad',
             'Day s Dessert', 'Day s Diabetic Dessert',
             'Day s Pudding', 'Day s Compote'])
        response = self.client.get('/delivery/kitchen_count/')
        self.assertTrue(b'Ground porc' in response.content)

    def test_no_components(self):
        """No orders on this day therefore no component summary"""
        response = self.client.get('/delivery/kitchen_count/2015/05/21/')
        self.assertTrue(b'SUBTOTAL' not in response.content)

    def test_labels_show_restrictions(self):
        """An ingredient we know will clash must be in the labels"""
        # generate orders today
        self.today = datetime.date.today()
        clients = Client.active.all()
        numorders = Order.objects.auto_create_orders(
            self.today, clients)
        Menu.create_menu_and_components(
            self.today,
            ['Ginger pork',
             'Green Salad', 'Fruit Salad',
             'Day s Dessert', 'Day s Diabetic Dessert',
             'Day s Pudding', 'Day s Compote'])

        self.client.get('/delivery/kitchen_count/')
        response = self.client.get('/delivery/viewMealLabels/')
        self.assertTrue('ReportLab' in repr(response.content))


class ChooseDayMainDishIngredientsTestCase(SousChefTestMixin, TestCase):

    fixtures = ['sample_data']

    @classmethod
    def setUpTestData(cls):
        # This data set includes 'Ginger pork' main dish
        # This data set includes 'Coq au vin' main dish
        # This data set includes 'Ground porc' main dish ingredient
        # This data set includes 'Pepper' available ingredient
        # create orders for today
        clients = Client.active.all()
        Order.objects.auto_create_orders(
            datetime.date.today(),
            clients)

    def setUp(self):
        self.force_login()

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
        req['sides_ingredients'] = [
            Ingredient.objects.filter(name='zucchini').first().id]
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
        req['sides_ingredients'] = [
            Ingredient.objects.filter(name='Onions').first().id]
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        response = self.client.get(reverse_lazy('delivery:kitchen_count'))
        self.assertTrue(b'Ginger pork' in response.content)
        response = self.client.get(reverse_lazy('delivery:meal'))
        self.assertTrue(b'Ginger pork' in response.content)

    def test_restore_dish_recipe(self):
        """Restore dish ingredients to those of recipe."""
        # dish : Ginger pork with added Spinach
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
        req['sides_ingredients'] = [Ingredient.objects.all().first().id]
        response = self.client.post(reverse_lazy('delivery:meal'), req)
        # restore recipe
        req = {}
        req['_restore'] = 'Restore recipe'
        req['maindish'] = str(maindish.id)
        req['sides_ingredients'] = [Ingredient.objects.all().first().id]
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
        req['sides_ingredients'] = [Ingredient.objects.all().first().id]
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


class DeliveryRouteSheetTestCase(SousChefTestMixin, TestCase):

    fixtures = ['sample_data']

    def setUp(self):
        # This data set includes 'Blondin' client lastname
        # generate orders today
        self.today = datetime.date.today()
        clients = Client.active.all()
        numorders = Order.objects.auto_create_orders(
            self.today, clients)
        self.route_id = Route.objects.get(name='Centre Sud').id
        self.force_login()

    def test_query(self):
        """Sample route sheet query."""
        route_list = Order.get_delivery_list(self.today, self.route_id)
        self.assertTrue('Blondin' in repr(route_list))

    def test_sheet(self):
        """Sample route sheet page."""
        member = Member.objects.filter(lastname='Blondin')[0]
        dic = {"route": [{"id": self.route_id}],
               "members": [{"id": member.id}]}
        response = self.client.post(reverse_lazy('delivery:save_route'),
                                    json.dumps(dic),
                                    content_type="application/json")
        response = self.client.get(
            reverse_lazy('delivery:route_sheet_id', args=[self.route_id]))
        self.assertTrue(b'Blondin' in response.content)


class RouteSequencingTestCase(SousChefTestMixin, TestCase):

    fixtures = ['sample_data']

    def setUp(self):
        self.force_login()
        # This data set includes 'Dallaire' and 'Taylor' client lastnames
        # generate orders today
        self.today = datetime.date.today()
        clients = Client.active.all()
        numorders = Order.objects.auto_create_orders(
            self.today, clients)
        self.route_id = Route.objects.get(name='Mile-End').id

    def test_get_orders_euclidean(self):
        """Route get orders with Euclidean optimized sequence."""
        response = self.client.get(
            '/delivery/getDailyOrders/?route=' +
            str(self.route_id) + '&mode=euclidean')
        self.assertTrue(b'Dallaire' in response.content)

    def test_save_route(self):
        """Route save sequence."""
        dic = {"route": [{"id": "4"}],
               "members": [{"id": 864}, {"id": 867}, {"id": 868},
                           {"id": 869}, {"id": 861}, {"id": 862}, {"id": 863}]}
        response = self.client.post(reverse_lazy('delivery:save_route'),
                                    json.dumps(dic),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'"OK"', response.content)

    def test_save_route_and_retrieve(self):
        """Route sequence save then retrieve."""
        mem_dal = Member.objects.filter(lastname='Dallaire')[0]
        mem_tay = Member.objects.filter(lastname='Taylor')[0]
        dic = {"route": [{"id": self.route_id}],
               "members": [{"id": mem_dal.id}, {"id": mem_tay.id}]}
        response = self.client.post(reverse_lazy('delivery:save_route'),
                                    json.dumps(dic),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'"OK"', response.content)
        response = self.client.get(
            '/delivery/getDailyOrders/?route=' +
            str(self.route_id) + '&if_exist_then_retrieve=true')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode(response.charset)
        waypoints = json.loads(content)['waypoints']
        self.assertEqual(waypoints[0]['id'], mem_dal.id)
        self.assertEqual(waypoints[1]['id'], mem_tay.id)

    def test_route_sequence_not_saved(self):
        """Attempt retrieving a route sequence that was not saved."""
        route_id_none = Route.objects.get(name='Centre Sud').id
        with self.assertRaises(Exception) as cm:
            response = self.client.get(
                '/delivery/getDailyOrders/?route=' +
                str(route_id_none) + '&if_exist_then_retrieve=true')
        self.assertIn('unknown', str(cm.exception))

    def test_get_orders_unknown_mode(self):
        """Route get orders with unknown transportation mode."""
        with self.assertRaises(Exception) as cm:
            response = self.client.get(
                '/delivery/getDailyOrders/?route=' +
                str(self.route_id) + '&mode=swimming')


class RedirectAnonymousUserTestCase(SousChefTestMixin, TestCase):

    fixtures = ['sample_data']

    def test_anonymous_user_gets_redirect_to_login_page(self):
        check = self.assertRedirectsWithAllMethods
        check(reverse('delivery:order'))
        check(reverse('delivery:meal'))
        meal = Component.objects.first()
        meal_id = meal.id
        check(reverse('delivery:meal_id', kwargs={'id': meal_id}))
        check(reverse('delivery:route'))
        check(reverse('delivery:routes'))
        check(reverse('delivery:organize_route', kwargs={'id': 1}))
        check(reverse('delivery:kitchen_count'))
        check(reverse('delivery:kitchen_count_date', kwargs={
            'year': 2016,
            'month': 11,
            'day': 30
        }))
        check(reverse('delivery:mealLabels'))
        check(reverse('delivery:route_sheet_id', kwargs={'id': 1}))
        check(reverse('delivery:dailyOrders'))
        check(reverse('delivery:refresh_orders'))
        check(reverse('delivery:save_route'))


class OrderlistViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['sample_data']

    def setUp(self):
        super(OrderlistViewTestCase, self).setUp()
        self.force_login()

    def test_can_filter_orders_by_client_names(self):
        # Setup
        Order.objects.all().update(delivery_date=tz.now())
        url = reverse('delivery:order')
        # Run
        response = self.client.get(url, {'client_name': 'john'})
        # Check
        self.assertEqual(
            set(response.context['orders']),
            set(Order.objects.filter(
                Q(client__member__firstname__icontains='john') |
                Q(client__member__lastname__icontains='john')
            )))


class KitchenCountOrderFilterTestCase(SousChefTestMixin, TestCase):
    fixtures = ['sample_data']

    def setUp(self):
        super(KitchenCountOrderFilterTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_can_filter_orders_by_client_names(self):
        # Setup
        queryset = Order.objects.all()
        request_1 = self.factory.get('/')
        request_2 = self.factory.get('/', {'client_name': 'john doe'})
        # Run
        filterset_1 = KitchenCountOrderFilter(request_1.GET, queryset)
        filterset_2 = KitchenCountOrderFilter(request_2.GET, queryset)
        # Check
        self.assertEqual(filterset_1.qs.count(), queryset.count())
        self.assertTrue(filterset_2.qs.count())
        self.assertEqual(
            set(filterset_2.qs),
            set(Order.objects.filter(
                Q(client__member__firstname__icontains='john') |
                Q(client__member__firstname__icontains='doe') |
                Q(client__member__lastname__icontains='john') |
                Q(client__member__lastname__icontains='doe')
            )))


class RoutesInformationViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['sample_data']

    def setUp(self):
        super(RoutesInformationViewTestCase, self).setUp()
        self.force_login()

    def test_can_embed_additional_route_sheet_information_when_printing(self):
        # Setup
        url = reverse('delivery:routes')
        # Run
        response_1 = self.client.get(url)
        response_2 = self.client.get(url, {'print': 'yes'})
        # Check
        self.assertNotIn('routes_dict', response_1.context)
        self.assertIn('routes_dict', response_2.context)
