import json

from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management import call_command
from django.forms import BaseFormSet
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.six import StringIO
from django.test import TestCase, Client

from member.models import (
    Member, Client, Address,
    Contact, Option, Client_option, Restriction, Route,
    Client_avoid_ingredient, Client_avoid_component,
    ClientScheduledStatus, Relationship,
    CELL, HOME, EMAIL, DAYS_OF_WEEK
)
from meal.models import (
    Restricted_item, Ingredient, Component, COMPONENT_GROUP_CHOICES
)
from order.models import Order
from member.factories import (
    RouteFactory, ClientFactory, ClientScheduledStatusFactory,
    MemberFactory, DeliveryHistoryFactory, RelationshipFactory
)
from meal.factories import IngredientFactory, ComponentFactory
from django.core.management import call_command
from django.utils.six import StringIO
from django.utils import translation
from django.utils.translation import ugettext

from order.factories import OrderFactory
from order.models import ORDER_STATUS_ORDERED
from member.forms import (
    ClientBasicInformation, ClientAddressInformation,
    ClientPaymentInformation,
    ClientRestrictionsInformation, ClientRelationshipInformation,
    ClientScheduledStatusForm
)
from sous_chef.tests import TestMigrations
from sous_chef.tests import TestMixin as SousChefTestMixin


def load_initial_data(client):
    """
    Load initial for the given client.
    """
    initial = {
        'firstname': client.member.firstname,
        'lastname': client.member.lastname,
        'alert': client.alert,
        'gender': client.gender,
        'language': client.language,
        'birthdate': client.birthdate,
        'home_phone': client.member.home_phone,
        'cell_phone': client.member.cell_phone,
        'email': client.member.email,
        'street': client.member.address.street,
        'city': client.member.address.city,
        'apartment': client.member.address.apartment,
        'postal_code': client.member.address.postal_code,
        'delivery_note': client.delivery_note,
        'route':
            client.route.id
            if client.route is not None
            else '',
        'latitude': client.member.address.latitude,
        'longitude': client.member.address.longitude,
        'distance': client.member.address.distance,
        'member': client.id,
        'same_as_client': True,
        'facturation': '',
        'billing_payment_type': '',

    }
    return initial


class MemberContact(TestCase):

    """
    Contact information data should be attached to members.
    Three types of data: EMAIL, CELL and HOME.
    """

    @classmethod
    def setUpTestData(cls):
        cls.member = MemberFactory()

    def test_home_phone(self):
        """
        Test that the factory properly sets a home phone information.
        """
        self.assertNotEqual(self.member.home_phone, "")

    def test_add_contact_information(self):
        """
        Test the add_contact_information method when no contact information
        of the given type exists yet.
        It is supposed to return TRUE if a new contact information is created.
        """
        self.assertTrue(
            self.member.add_contact_information(CELL, '438-000-0000')
        )
        self.assertEqual(self.member.cell_phone, '438-000-0000')
        self.assertTrue(
            self.member.add_contact_information(EMAIL, 'admin@example.com')
        )
        self.assertEqual(self.member.email, 'admin@example.com')

    def test_add_contact_information_empty(self):
        """
        Passing an empty value should not update nor create anything, unless
        the force_update parameter was passed.
        """
        self.member.add_contact_information(CELL, '438-000-0000')
        self.assertEqual(self.member.cell_phone, '438-000-0000')
        self.assertFalse(
            self.member.add_contact_information(CELL, '')
        )
        self.assertEqual(self.member.cell_phone, '438-000-0000')
        self.assertFalse(
            self.member.add_contact_information(CELL, '', True)
        )
        self.assertEqual(self.member.cell_phone, '')

    def test_update_contact_information(self):
        """
        Test the add_contact_information method when a contact information
        of the given type already exists. The contact information should be
        updated, instead of creating a new one.
        """
        self.assertFalse(
            self.member.add_contact_information(HOME, '514-000-0000')
        )
        self.assertEqual(self.member.home_phone, '514-000-0000')


class MemberTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        member = Member.objects.create(
            firstname='Katrina', lastname='Heide')
        Contact.objects.create(
            type='Home phone', value='514-456-7890', member=member)

        Contact.objects.create(
            type='Cell phone', value='555-555-4444', member=member
        )

        Contact.objects.create(
            type='Work phone', value='555-444-5555', member=member
        )

        Contact.objects.create(
            type='Email', value='test@test.com', member=member
        )

    def test_str_is_fullname(self):
        """A member must be listed using his/her fullname"""
        member = Member.objects.get(firstname='Katrina')
        str_member = str(member)
        self.assertEqual(str_member, 'Katrina Heide')

    def test_home_phone(self):
        """Test that the home phone property is valid"""
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.home_phone, '514-456-7890')

    def test_cell_phone(self):
        """Test that the cell phone property is valid"""
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.cell_phone, '555-555-4444')

    def test_work_phone(self):
        """Test that the work phone property is valid"""
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.work_phone, '555-444-5555')

    def test_email(self):
        """Test that the email property is valid"""
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.email, "test@test.com")


class ContactTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        member = Member.objects.create(
            firstname='Katrina', lastname='Heide')
        Contact.objects.create(
            type='Home phone', value='514-456-7890', member=member)

    def test_str_is_fullname(self):
        """A contact must be listed using his/her fullname"""
        member = Member.objects.get(firstname='Katrina')
        contact = Contact.objects.get(member=member)
        self.assertTrue(member.firstname in str(contact))
        self.assertTrue(member.lastname in str(contact))


class AddressTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5')
        Member.objects.create(
            firstname='Katrina', lastname='Heide',
            address=address)

    def test_str_includes_street(self):
        """An address listing must include the street name"""
        member = Member.objects.get(firstname='Katrina')
        # address = Address.objects.get(member=member)
        self.assertTrue('De Bullion' in str(member.address))


class ClientTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        today = date.today()
        cls.ss_client = ClientFactory(
            birthdate=date(today.year - 40, today.month, today.day),
            meal_default_week={
                'monday_size': 'L',
                'monday_main_dish_quantity': 1
            }
        )
        cls.order = OrderFactory(
            client=cls.ss_client
        )

    def test_str_is_fullname(self):
        """A client must be listed using his/her fullname"""
        self.assertTrue(self.ss_client.member.firstname in str(self.ss_client))
        self.assertTrue(self.ss_client.member.lastname in str(self.ss_client))

    def test_is_geolocalized(self):
        self.assertTrue(self.ss_client.is_geolocalized)

    def test_age(self):
        """The age on given date is properly computed"""
        self.assertEqual(self.ss_client.age, 40)
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        self.ss_client.birthdate = date(yesterday.year - 40, yesterday.month,
                                        yesterday.day)
        self.ss_client.save()
        self.assertEqual(Client.objects.get(id=self.ss_client.id).age, 40)
        self.ss_client.birthdate = date(tomorrow.year - 40, tomorrow.month,
                                        tomorrow.day)
        self.ss_client.save()
        self.assertEqual(Client.objects.get(id=self.ss_client.id).age, 39)

    def test_orders(self):
        """Orders of a given client must be available as a model property"""
        self.assertEqual(self.ss_client.orders.count(), 1)
        self.assertEqual(
            self.ss_client.orders.first().creation_date,
            date.today())

    def test_meal_default(self):
        # monday_size = 'L'
        self.assertEqual(self.ss_client.meal_default_week['monday_size'], 'L')

        # monday_main_dish_quantity = 1
        self.assertEqual(
            self.ss_client.meal_default_week['monday_main_dish_quantity'], 1
        )

    def test_delete_route(self):
        route = Route.objects.get(name=self.ss_client.route.name)
        route.delete()
        # We reload our client to update its informations
        client = Client.objects.get(id=self.ss_client.id)
        self.assertEqual(
            client.route, None
        )


class OptionTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Option.objects.create(
            name='PUREE ALL', option_group='preparation')

    def test_str_is_fullname(self):
        """Option's string representation is its name"""
        name = 'PUREE ALL'
        option = Option.objects.get(name=name)
        self.assertEqual(name, str(option))


class ClientOptionTestCase(TestCase):

    fixtures = ['routes']

    @classmethod
    def setUpTestData(cls):
        cls.clientTest = ClientFactory()
        option = Option.objects.create(
            name='PUREE ALL', option_group='preparation')
        meals_schedule_option = Option.objects.create(
            name='meals_schedule', option_group='dish'
        )
        Client_option.objects.create(client=cls.clientTest, option=option)
        Client_option.objects.create(
            client=cls.clientTest,
            option=meals_schedule_option,
            value=json.dumps(['monday', 'wednesday', 'friday']),
        )

    def test_str_includes_all_names(self):
        """
        A Client_option's string representation includes the name
        of the client and the name of the option.
        """
        name = 'PUREE ALL'
        option = Option.objects.get(name=name)
        client_option = Client_option.objects.get(
            client=self.clientTest, option=option)
        self.assertTrue(self.clientTest.member.firstname in str(client_option))
        self.assertTrue(self.clientTest.member.lastname in str(client_option))
        self.assertTrue(option.name in str(client_option))

    def test_meals_schedule_option(self):
        """
        Meals schedule must be saved as a client option.
        """
        self.assertEqual(
            self.clientTest.simple_meals_schedule,
            ['monday', 'wednesday', 'friday']
        )


class ClientMealDefaultWeekTestCase(TestCase):
    fixtures = ['routes']

    @classmethod
    def setUpTestData(cls):
        cls.clientTest = ClientFactory(
            delivery_type="O",
            meal_default_week={
                "main_dish_monday_quantity": 1,
                "size_monday": "R",
                "diabetic_monday_quantity": 2,
                "fruit_salad_monday_quantity": 1,

                "main_dish_tuesday_quantity": 0,
                "size_tuesday": "L",
                "compote_tuesday_quantity": 1,

                "main_dish_wednesday_quantity": 0,
                "dessert_wednesday_quantity": 0,
                "size_wednesday": "R",

                "main_dish_thursday_quantity": 1,
                "diabetic_thursday_quantity": 2,
                "fruit_salad_thursday_quantity": 1,

                # friday, saturday, sunday nothing
            }
        )
        meals_schedule_option = Option.objects.create(
            name='meals_schedule', option_group='dish'
        )
        cls.clientOptionTest = Client_option.objects.create(
            client=cls.clientTest,
            option=meals_schedule_option,
            value=json.dumps(['monday', 'wednesday', 'friday']),
        )

    def test_client_meals_default(self):
        """
        Tests: Client.meals_default
        """
        md = dict(self.clientTest.meals_default)
        self.assertEqual(md['monday'], {
            'main_dish': 1,
            'size': 'R',
            'dessert': None,
            'diabetic': 2,
            'fruit_salad': 1,
            'green_salad': None,
            'pudding': None,
            'compote': None
        })
        self.assertEqual(md['tuesday'], {
            'main_dish': 0,  # Client said zero
            'size': 'L',
            'dessert': None,
            'diabetic': None,
            'fruit_salad': None,
            'green_salad': None,
            'pudding': None,
            'compote': 1
        })
        self.assertEqual(md['wednesday'], {
            'main_dish': 0,  # Client said zero
            'size': 'R',
            'dessert': 0,    # Client said zero
            'diabetic': None,
            'fruit_salad': None,
            'green_salad': None,
            'pudding': None,
            'compote': None
        })
        self.assertEqual(md['thursday'], {
            'main_dish': 1,
            'size': None,
            'dessert': None,
            'diabetic': 2,
            'fruit_salad': 1,
            'green_salad': None,
            'pudding': None,
            'compote': None
        })
        not_set = {
            'main_dish': None,
            'size': None,
            'dessert': None,
            'diabetic': None,
            'fruit_salad': None,
            'green_salad': None,
            'pudding': None,
            'compote': None
        }
        self.assertEqual(md['friday'], not_set)
        self.assertEqual(md['saturday'], not_set)
        self.assertEqual(md['sunday'], not_set)

    def test_client_meals_schedule(self):
        """
        Tests: Client.meals_schedule
        """
        ms = dict(self.clientTest.meals_schedule)
        self.assertEqual(ms['monday'], {
            'main_dish': 1,
            'size': 'R',
            'dessert': None,
            'diabetic': 2,
            'fruit_salad': 1,
            'green_salad': None,
            'pudding': None,
            'compote': None
        })
        self.assertEqual(ms['wednesday'], {
            'main_dish': 0,  # Client said zero
            'size': 'R',
            'dessert': 0,    # Client said zero
            'diabetic': None,
            'fruit_salad': None,
            'green_salad': None,
            'pudding': None,
            'compote': None
        })
        self.assertEqual(ms['friday'], {
            'main_dish': None,
            'size': None,
            'dessert': None,
            'diabetic': None,
            'fruit_salad': None,
            'green_salad': None,
            'pudding': None,
            'compote': None
        })
        self.assertNotIn('tuesday', ms)
        self.assertNotIn('thursday', ms)
        self.assertNotIn('saturday', ms)
        self.assertNotIn('sunday', ms)

    def test_client_meals_schedule_without_option(self):
        """
        Test when the client option 'meals_schedule' is not set.
        """
        self.clientOptionTest.delete()
        ms = self.clientTest.meals_schedule
        self.assertEqual(ms, ())


class RestrictionTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5')
        member = Member.objects.create(firstname='Angela',
                                       lastname='Desousa',
                                       address=address)
        client = Client.objects.create(
            member=member, billing_member=member,
            birthdate=date(1980, 4, 19))
        restricted_item = Restricted_item.objects.create(
            name='pork', restricted_item_group='meat')
        Restriction.objects.create(client=client,
                                   restricted_item=restricted_item)

    def test_str_includes_all_names(self):
        """A restriction's string representation includes the name
        of the client and the name of the restricted_item.
        """
        member = Member.objects.get(firstname='Angela')
        client = Client.objects.get(member=member)
        name = 'pork'
        restricted_item = Restricted_item.objects.get(name=name)
        restriction = Restriction.objects.get(
            client=client, restricted_item=restricted_item)
        self.assertTrue(client.member.firstname in str(restriction))
        self.assertTrue(client.member.lastname in str(restriction))
        self.assertTrue(restricted_item.name in str(restriction))


class ClientAvoidIngredientTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5')
        member = Member.objects.create(firstname='Angela',
                                       lastname='Desousa',
                                       address=address)
        client = Client.objects.create(
            member=member, billing_member=member,
            birthdate=date(1980, 4, 19))
        ingredient = Ingredient.objects.create(
            name='ground pork')
        Client_avoid_ingredient.objects.create(client=client,
                                               ingredient=ingredient)

    def test_str_includes_all_names(self):
        """A client_avoid_ingredient's string representation includes the name
        of the client and the name of the ingredient.
        """
        member = Member.objects.get(firstname='Angela')
        client = Client.objects.get(member=member)
        name = 'ground pork'
        ingredient = Ingredient.objects.get(name=name)
        client_avoid_ingredient = Client_avoid_ingredient.objects.get(
            client=client, ingredient=ingredient)
        self.assertTrue(
            client.member.firstname in str(client_avoid_ingredient))
        self.assertTrue(client.member.lastname in str(client_avoid_ingredient))
        self.assertTrue(ingredient.name in str(client_avoid_ingredient))


class ClientAvoidComponentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5')
        member = Member.objects.create(firstname='Angela',
                                       lastname='Desousa',
                                       address=address)
        client = Client.objects.create(
            member=member, billing_member=member,
            birthdate=date(1980, 4, 19))
        component = Component.objects.create(
            name='ginger pork', component_group='main dish')
        Client_avoid_component.objects.create(client=client,
                                              component=component)

    def test_str_includes_all_names(self):
        """A client_avoid_component's string representation includes the name
        of the client and the name of the component.
        """
        member = Member.objects.get(firstname='Angela')
        client = Client.objects.get(member=member)
        name = 'ginger pork'
        component = Component.objects.get(name=name)
        client_avoid_component = Client_avoid_component.objects.get(
            client=client, component=component)
        self.assertTrue(client.member.firstname in str(client_avoid_component))
        self.assertTrue(client.member.lastname in str(client_avoid_component))
        self.assertTrue(component.name in str(client_avoid_component))


class FormTestCase(TestCase):

    fixtures = ['client_options.json']

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5'
        )
        Member.objects.create(
            firstname='First',
            lastname='Member',
            address=address
        )
        Member.objects.create(
            firstname='Second',
            lastname='Member'
        )
        cls.route = RouteFactory()
        cls.restricted_item_1 = Restricted_item.objects.create(
            name='pork', restricted_item_group='meat')
        cls.restricted_item_2 = Restricted_item.objects.create(
            name='soya', restricted_item_group='other')
        cls.food_preparation = Option.objects.create(
            name='PUREE ALL', option_group='preparation')
        cls.ingredient = IngredientFactory()
        cls.component = ComponentFactory()

    def setUp(self):
        self.client.login(username=self.admin.username, password='test1234')

    def tearDown(self):
        self.client.logout()

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('member:member_step')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 302)

    def test_acces_to_form(self):
        """Test if the form is accesible from its url"""
        result = self.client.get(
            reverse_lazy(
                'member:member_step'
            ), follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_basic_info(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext('basic_information')}
            ),
            follow=False
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_adress_information(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext('address_information')}
            ),
            follow=False
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_relationship_information(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext('relationships')}
            ),
            follow=False
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_payment_information(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': 'payment_information'}
            ),
            follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_dietary_restriction(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': 'dietary_restriction'}
            ),
            follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_emergency_contacts(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': 'emergency_contacts'}
            ),
            follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_form_save_data(self):
        basic_information_data = {
            "client_wizard-current_step": "basic_information",
            "basic_information-firstname": "User",
            "basic_information-lastname": "Testing",
            "basic_information-language": "fr",
            "basic_information-gender": "M",
            "basic_information-birthdate": "1990-12-12",
            "basic_information-home_phone": "555-555-5555",
            "basic_information-email": "test@example.com",
            "basic_information-cell_phone": "438-000-0000",
            "basic_information-alert": "Testing alert message",
            "wizard_goto_step": ""
        }

        address_information_data = {
            "client_wizard-current_step": "address_information",
            "address_information-street": "555 rue clark",
            "address_information-apartment": "222",
            "address_information-city": "montreal",
            "address_information-postal_code": "H3C 2C2",
            "address_information-route": self.route.id,
            "address_information-latitude": 45.5343077,
            "address_information-longitude": -73.620735,
            "address_information-distance": 4.062611162244175,
            "wizard_goto_step": "",
        }

        payment_information_data = {
            "client_wizard-current_step": "payment_information",
            "payment_information-same_as_client": False,
            "payment_information-firstname": "Billing",
            "payment_information-lastname": "Testing",
            "payment_information-billing_payment_type": "credit",
            "payment_information-facturation": "default",
            "payment_information-street": "111 rue clark",
            "payment_information-apartement": "222",
            "payment_information-city": "Montreal",
            "payment_information-postal_code": "H2C 3G4",
            "wizard_goto_step": "",
        }

        restriction_information_data = {
            "client_wizard-current_step": "dietary_restriction",
            "dietary_restriction-status": "on",
            "dietary_restriction-delivery_type": "O",
            "dietary_restriction-meals_schedule": ['monday', 'wednesday'],
            "dietary_restriction-meal_default": "1",
            "dietary_restriction-restrictions":
                [self.restricted_item_1.id, self.restricted_item_2.id],
            "dietary_restriction-food_preparation": self.food_preparation.id,
            "dietary_restriction-ingredient_to_avoid": self.ingredient.id,
            "dietary_restriction-dish_to_avoid": self.component.id,
            "wizard_goto_step": ""
        }
        for day in restriction_information_data[
                "dietary_restriction-meals_schedule"
        ]:
            restriction_information_data[
                'dietary_restriction-size_{}'.format(day)
            ] = 'R'
            for component, _ in COMPONENT_GROUP_CHOICES:
                name = "dietary_restriction-{}_{}_quantity".format(
                    component, day
                )
                restriction_information_data[name] = 1

        relationships_data = {
            "client_wizard-current_step": "relationships",
            "relationships-TOTAL_FORMS": "1",
            "relationships-INITIAL_FORMS": "1",
            "relationships-MIN_NUM_FORMS": "0",
            "relationships-MAX_NUM_FORMS": "1000",
            "relationships-0-firstname": "Relationship",
            "relationships-0-lastname": "Testing",
            "relationships-0-work_phone": "555-444-5555",
            "relationships-0-nature": "friend",
            "relationships-0-type": [
                Relationship.EMERGENCY, Relationship.REFERENT],
            "relationships-0-work_information": "CLSC",
            "relationships-0-referral_date": "2012-12-12",
            "relationships-0-referral_reason": "Testing referral reason",
        }

        stepsdata = [
            ('basic_information', basic_information_data),
            ('address_information', address_information_data),
            ('relationships', relationships_data),
            ('payment_information', payment_information_data),
            ('dietary_restriction', restriction_information_data),
        ]

        for step, data in stepsdata:
            response = self.client.post(
                reverse_lazy('member:member_step',
                             kwargs={'step': ugettext(step)}),
                data,
                follow=True
            )

        member = Member.objects.get(firstname="User")
        self._test_assert_member_info(member)

        client = Client.objects.get(member=member)
        self._test_assert_client_info(client)

        # Test the client view
        self._test_client_detail_view(client)
        self._test_client_view_preferences(client)

    def _test_assert_member_info(self, member):
        # test firstname and lastname
        self.assertEqual(member.firstname, "User")
        self.assertEqual(member.lastname, "Testing")

        # test_home_phone_member:
        self.assertTrue(member.home_phone.startswith('555'))
        self.assertEqual(member.email, 'test@example.com')
        self.assertEqual(member.cell_phone, '438-000-0000')

        # test_client_contact_type:
        self.assertEqual(member.member_contact.first().type, "Home phone")

        # test_client_address:
        self.assertEqual(member.address.street, "555 rue clark")
        self.assertEqual(member.address.postal_code, "H3C 2C2")
        self.assertEqual(member.address.apartment, "222")
        self.assertEqual(member.address.city, "montreal")

    def _test_assert_client_info(self, client):
        # test_client_alert:
        self.assertEqual(client.alert, "Testing alert message")

        # test_client_languages:
        self.assertEqual(client.language, "fr")

        # test_client_birthdate:
        self.assertEqual(client.birthdate, date(1990, 12, 12))

        # test_client_gender:
        self.assertEqual(client.gender, "M")

        # test client delivery type
        self.assertEqual(client.delivery_type, 'O')

        # test_relationship_name:
        self.assertEqual(
            client.relationship_set.first().member.firstname,
            "Relationship"
        )
        self.assertEqual(
            client.relationship_set.first().member.lastname,
            "Testing"
        )

        # test relationship contact infos (email and work phone)
        self.assertEqual(
            client.relationship_set.first().member.work_phone,
            "555-444-5555"
        )

        # test_relationship_referent_work_information:
        self.assertEqual(
            client.relationship_set.first().member.work_information,
            "CLSC"
        )

        # test_referral_extras:
        self.assertEqual(
            client.relationship_set.first().extra_fields, {
                'referral_date': '2012-12-12',
                'referral_reason': "Testing referral reason"})

        # test_billing_name:
        self.assertEqual(client.billing_member.firstname, "Billing")
        self.assertEqual(client.billing_member.lastname, "Testing")

        #  test_billing_type:
        self.assertEqual(client.billing_payment_type, "credit")

        #  test_billing_address:
        self.assertEqual(client.billing_member.address.city, "Montreal")
        self.assertEqual(client.billing_member.address.street, "111 rue clark")
        self.assertEqual(client.billing_member.address.postal_code, "H2C 3G4")

        #  test_billing_rate_type:
        self.assertEqual(client.rate_type, 'default')

        # Test meals schedule
        self.assertEqual(client.simple_meals_schedule, ['monday', 'wednesday'])

        # test_restrictions
        restriction_1 = Restriction.objects.get(
            client=client, restricted_item=self.restricted_item_1)
        restriction_2 = Restriction.objects.get(
            client=client, restricted_item=self.restricted_item_2)
        self.assertTrue(self.restricted_item_1.name in str(restriction_1))
        self.assertTrue(self.restricted_item_2.name in str(restriction_2))

        # Test food preparation
        food_preparation = Client_option.objects.get(
            client=client,
            option=self.food_preparation
        )
        self.assertTrue(self.food_preparation.name in str(food_preparation))

        # Test for ingredients to avoid
        self.assertTrue(self.ingredient in set(client.ingredients_to_avoid.all()))  # noqa

        # Test for components to avoid
        self.assertTrue(self.component in set(client.components_to_avoid.all()))  # noqa

    """
    Test that the meals preferences are properly displayed.
    """

    def _test_client_view_preferences(self, client):
        resp = self.client.get(
            reverse_lazy('member:client_allergies', kwargs={'pk': client.id})
        )

        # self.assertContains(resp, client.get_status_display)
        self.assertContains(resp, self.restricted_item_1)
        self.assertContains(resp, self.restricted_item_2)
        self.assertContains(resp, self.food_preparation)
        self.assertContains(resp, self.ingredient.name)
        self.assertContains(resp, self.component.name)

    def _test_client_detail_view(self, client):
        response = self.client.get(
            reverse_lazy('member:client_information', kwargs={'pk': client.id})
        )

        self.assertTrue(b"User" in response.content)
        self.assertTrue(b"Testing" in response.content)
        self.assertTrue(b"Home phone" in response.content)
        self.assertTrue(b"555 rue clark" in response.content)
        self.assertTrue(b"H3C 2C2" in response.content)
        self.assertTrue(b"montreal" in response.content)
        self.assertTrue(b"Testing alert message" in response.content)
        self.assertTrue(b"555-444-5555" in response.content)

    def test_form_validate_data(self):
        """Test all the step of the form with and without wrong data"""
        self._test_basic_information_with_errors()
        self._test_basic_information_without_errors()
        self._test_address_information_with_errors()
        self._test_address_information_without_errors()
        self._test_step_relationships_with_errors()
        self._test_step_relationships_without_errors()
        self._test_payment_information_with_errors()
        self._test_payment_information_without_errors()
        self._test_step_dietary_restriction_with_errors()
        self._test_step_dietary_restriction_without_errors()

    def _test_basic_information_with_errors(self):
        # Data for the basic_information step with errors.
        basic_information_data_with_error = {
            "client_wizard-current_step": "basic_information",
            "basic_information-firstname": "User",
            "basic_information-lastname": "",
            "basic_information-language": "fr",
            "basic_information-gender": "M",
            "basic_information-birthdate": "",
            "basic_information-alert": "",
            "wizard_goto_step": ""
        }

        # Send the data to the form.
        error_response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "basic_information"}
            ),
            basic_information_data_with_error,
            follow=True
        )

        # The response is the same form with the errors messages.
        self.assertTrue(error_response.context['form'].errors)
        self.assertFormError(error_response, 'form',
                             'lastname',
                             ugettext('This field is required.'))
        self.assertFormError(error_response, 'form',
                             'birthdate',
                             ugettext('This field is required.'))
        self.assertFormError(error_response, 'form',
                             'email',
                             ugettext('At least one contact information '
                                      'is required.'))
        self.assertFormError(error_response, 'form',
                             'home_phone',
                             ugettext('At least one contact information '
                                      'is required.'))
        self.assertFormError(error_response, 'form',
                             'cell_phone',
                             ugettext('At least one contact information '
                                      'is required.'))

    def _test_basic_information_without_errors(self):
        # Data for the basic_information step without errors.
        basic_information_data = {
            "client_wizard-current_step": "basic_info",
            "basic_information-firstname": "User",
            "basic_information-lastname": "Testing",
            "basic_information-language": "fr",
            "basic_information-gender": "M",
            "basic_information-birthdate": "1990-12-12",
            "basic_information-home_phone": "555-555-5555",
            "basic_information-alert": "Testing alert message",
            "wizard_goto_step": ""
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("basic_information")}
            ),
            basic_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': ugettext("address_information")}
        ))

        # The response is the next step of the form with no errors messages.
        form = response.context['form']
        self.assertFalse(form.errors)
        self.assertNotIn('gender', form.fields)
        self.assertNotIn('home_phone', form.fields)
        self.assertNotIn('contact_value', form.fields)
        # New form field in the next step
        self.assertIn('street', form.fields)

    def _test_address_information_with_errors(self):
        # Data for the address_information step with errors.
        address_information_data_with_error = {
            "client_wizard-current_step": "address_information",
            "address_information-street": "",
            "address_information-apartment": "",
            "address_information-city": "",
            "address_information-postal_code": "",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("address_information")}
            ),
            address_information_data_with_error,
            follow=True
        )

        # The response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'street',
                             ugettext('This field is required.'))
        self.assertFormError(response_error, 'form',
                             'city',
                             ugettext('This field is required.'))
        self.assertFormError(response_error, 'form',
                             'postal_code',
                             ugettext('This field is required.'))

    def _test_address_information_without_errors(self):
        # Data for the address_information step without errors.
        address_information_data = {
            "client_wizard-current_step": "address_information",
            "address_information-street": "555 rue clark",
            "address_information-apartment": "222",
            "address_information-city": "montreal",
            "address_information-postal_code": "H3C2C2",
            "address_information-route": self.route.id,
            "address_information-latitude": 45.5343077,
            "address_information-longitude": -73.620735,
            "address_information-distance": 4.062611162244175,
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("address_information")}),
            address_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse(
            'member:member_step',
            kwargs={'step': ugettext("relationships")}
        ))

        # The response is the next step of the form with no errors messages.
        form = response.context['form']
        self.assertFalse(form.errors)
        self.assertEqual(form.prefix, 'relationships')

    def _test_step_relationships_with_errors(self):
        # Data for the address_information step with errors.
        emergency_contact_data_with_error = {
            "client_wizard-current_step": "relationships",
            "relationships-TOTAL_FORMS": "1",
            "relationships-INITIAL_FORMS": "1",
            "relationships-MIN_NUM_FORMS": "0",
            "relationships-MAX_NUM_FORMS": "1000",
            "relationships-0-firstname": "",
            "relationships-0-lastname": "",
            "relationships-0-work_phone": "",
            "relationships-0-nature": "",
            "relationships-0-type": [
                Relationship.EMERGENCY, Relationship.REFERENT],
            "relationships-0-work_information": "",
            "relationships-0-referral_date": "",
            "relationships-0-referral_reason": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("relationships")}
            ),
            emergency_contact_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormsetError(response_error, 'form', 0,
                                'cell_phone',
                                ugettext('At least one contact '
                                         'is required.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'work_phone',
                                ugettext('At least one contact '
                                         'is required.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'email',
                                ugettext('At least one contact '
                                         'is required.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'lastname',
                                ugettext('This field is required unless '
                                         'you chose an existing member.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'firstname',
                                ugettext('This field is required unless '
                                         'you chose an existing member.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'firstname',
                                ugettext('This field is required unless '
                                         'you chose an existing member.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'work_information',
                                ugettext('This field is required '
                                         'for a referent relationship.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'referral_date',
                                ugettext('This field is required '
                                         'for a referent relationship.'))
        self.assertFormsetError(response_error, 'form', 0,
                                'referral_reason',
                                ugettext('This field is required '
                                         'for a referent relationship.'))

    def _test_step_relationships_without_errors(self):
        # Data for the address_information step without errors.
        pk = Member.objects.get(firstname="First").id
        relationships_data = {
            "client_wizard-current_step": "relationships",
            "relationships-TOTAL_FORMS": "1",
            "relationships-INITIAL_FORMS": "1",
            "relationships-MIN_NUM_FORMS": "0",
            "relationships-MAX_NUM_FORMS": "1000",
            "relationships-0-member": "[{}] First Member".format(pk),
            "relationships-0-firstname": "",
            "relationships-0-lastname": "",
            "relationships-0-work_phone": "",
            "relationships-0-work_information": "",
            "relationships-0-nature": "friend",
            "relationships-0-type": [
                Relationship.EMERGENCY, Relationship.REFERENT],
            "relationships-0-referral_date": "2012-12-12",
            "relationships-0-referral_reason": "Test reason",
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("relationships")}
            ),
            relationships_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': ugettext("payment_information")}
        ))

        # The response is the next step of the form with no errors messages.
        form = response.context['form']
        self.assertFalse(form.errors)
        self.assertNotIn('work_information', form.fields)
        # New form field in the next step
        self.assertIn('billing_payment_type', form.fields)
        self.assertIn('facturation', form.fields)

    def _test_payment_information_with_errors(self):
        # Data for the address_information step with errors.
        pk = Member.objects.get(firstname="Second").id
        payment_information_data_with_error = {
            "client_wizard-current_step": "payment_information",
            "payment_information-member": "[{}] Second Member".format(pk),
            "payment_information-firstname": "",
            "payment_information-lastname": "",
            "payment_information-billing_payment_type": "INVALID",
            "payment_information-facturation": "default",
            "payment_information-street": "",
            "payment_information-apartement": "",
            "payment_information-city": "",
            "payment_information-postal_code": "",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("payment_information")}
            ),
            payment_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'billing_payment_type',
                             ugettext('Select a valid choice. %(value)s is '
                                      'not one of the available '
                                      'choices.') % {'value': 'INVALID'})
        self.assertFormError(response_error, 'form',
                             'member',
                             ugettext('This member has not a valid address, '
                                      'please add a valid address to this '
                                      'member, '
                                      'so it can be used for the billing.'))

        # Data for the address_information step with errors.
        payment_information_data_with_error = {
            "client_wizard-current_step": "payment_information",
            "payment_information-member": "",
            "payment_information-firstname": "Third",
            "payment_information-lastname": "Member",
            "payment_information-billing_payment_type": "cheque",
            "payment_information-facturation": "default",
            "payment_information-street": "",
            "payment_information-apartement": "",
            "payment_information-city": "",
            "payment_information-postal_code": "",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("payment_information")}
            ),
            payment_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'street',
                             ugettext('This field is required'))
        self.assertFormError(response_error, 'form',
                             'city',
                             ugettext('This field is required'))
        self.assertFormError(response_error, 'form',
                             'postal_code',
                             ugettext('This field is required'))

    def _test_payment_information_without_errors(self):
        # Data for the address_information step without errors.
        pk = Member.objects.get(firstname="First").id
        payment_information_data = {
            "client_wizard-current_step": "payment_information",
            "payment_information-member": "[{}] First Member".format(pk),
            "payment_information-firstname": "",
            "payment_information-lastname": "",
            "payment_information-billing_payment_type": "3rd",
            "payment_information-facturation": "default",
            "payment_information-street": "",
            "payment_information-apartement": "",
            "payment_information-city": "",
            "payment_information-postal_code": "",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("payment_information")}
            ),
            payment_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse(
            'member:member_step',
            kwargs={'step': ugettext("dietary_restriction")}
        ))

        # The response is the next step of the form with no errors messages.
        form = response.context['form']
        self.assertFalse(form.errors)
        self.assertNotIn('billing_payment_type', form.fields)
        self.assertNotIn('facturation', form.fields)
        # New form field in the next step
        self.assertIn('status', form.fields)

    def _test_step_dietary_restriction_with_errors(self):
        # Data for the address_information step with errors.
        restriction_information_data_with_error = {
            "client_wizard-current_step": "dietary_restriction",
            "dietary_restriction-status": "",
            "dietary_restriction-delivery_type": "",
            "dietary_restriction-meals_schedule": "",
            "dietary_restriction-meal_default": "",
            "wizard_goto_step": ""
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("dietary_restriction")}
            ),
            restriction_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'delivery_type',
                             ugettext('This field is required.'))
        self.assertFormError(response_error, 'form',
                             'meals_schedule',
                             ugettext('Select a valid choice. %(value)s is '
                                      'not one of the available '
                                      'choices.') % {'value': ''})

    def _test_step_dietary_restriction_without_errors(self):
        # Data for the address_information step without errors.
        restriction_information_data = {
            "client_wizard-current_step": "dietary_restriction",
            "dietary_restriction-status": "on",
            "dietary_restriction-delivery_type": "O",
            "dietary_restriction-meals_schedule": "monday",
            "dietary_restriction-meal_default": "1",
            "wizard_goto_step": ""
        }
        for day in [restriction_information_data[
                "dietary_restriction-meals_schedule"
        ]]:
            restriction_information_data[
                'dietary_restriction-size_{}'.format(day)
            ] = 'R'
            for component, _ in COMPONENT_GROUP_CHOICES:
                name = "dietary_restriction-{}_{}_quantity".format(
                    component, day
                )
                restriction_information_data[name] = 1

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': ugettext("dietary_restriction")}
            ),
            restriction_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse('member:list'))

        # After final step: no forms anymore!
        self.assertNotIn('form', response.context)


class MemberSearchTestCase(SousChefTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        member = Member.objects.create(
            firstname='Katrina', lastname='Heide')
        Contact.objects.create(
            type='Home phone', value='514-456-7890', member=member)

    def setUp(self):
        self.force_login()

    def test_search_member_by_firstname(self):
        """
        A member must be find if the search use
        at least 3 characters of his first name
        """
        result = self.client.get(
            reverse_lazy('member:search') + '?name=Heid',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )
        self.assertTrue(b'Katrina Heide' in result.content)

    def test_search_member_by_lastname(self):
        """
        A member must be find if the search use
        at least 3 characters of his last name
        """
        result = self.client.get(
            reverse_lazy('member:search') + '?name=Katri',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )
        self.assertTrue(b'Katrina Heide' in result.content)


class ClientStatusUpdateAndScheduleCase(SousChefTestMixin, TestCase):

    fixtures = ['routes.json']

    def setUp(self):
        self.active_client = ClientFactory(status=Client.ACTIVE)
        self.stop_client = ClientFactory(status=Client.STOPNOCONTACT)

    def test_scheduled_change_is_valid(self):
        """
        A scheduled change is only valid if the client status matches with
        the status_from attribute of the schedules change.
        """
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
        )
        self.assertTrue(scheduled_change.is_valid())

    def test_scheduled_change_is_invalid(self):
        """
        A scheduled change is only valid if the client status matches with
        the status_from attribute of the schedules change.
        """
        scheduled_change = ClientScheduledStatusFactory(
            client=self.stop_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED
        )
        self.assertFalse(scheduled_change.is_valid())

    def test_scheduled_change_needs_attention(self):
        """
        Needs attention when the status is ERROR or the scheduled date has
        passed.
        """
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today() - timedelta(days=1),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
            operation_status=ClientScheduledStatus.TOBEPROCESSED
        )
        self.assertTrue(scheduled_change.needs_attention)
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
            operation_status=ClientScheduledStatus.ERROR
        )
        self.assertTrue(scheduled_change.needs_attention)
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
            operation_status=ClientScheduledStatus.TOBEPROCESSED
        )
        self.assertTrue(scheduled_change.needs_attention)
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today() + timedelta(days=1),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
            operation_status=ClientScheduledStatus.TOBEPROCESSED
        )
        self.assertFalse(scheduled_change.needs_attention)

    def test_scheduled_change_process_success(self):
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED
        )
        self.assertTrue(scheduled_change.process())
        self.assertEqual(
            scheduled_change.operation_status,
            ClientScheduledStatus.PROCESSED)
        self.assertEqual(self.active_client.status, Client.PAUSED)
        self.assertEqual(self.active_client.notes.count(), 1)
        self.assertEqual(self.active_client.notes.first().note,
                         scheduled_change.__str__())

    def test_scheduled_change_process_failed(self):
        scheduled_change = ClientScheduledStatusFactory(
            client=self.stop_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED
        )
        self.assertFalse(scheduled_change.process())
        self.assertEqual(
            scheduled_change.operation_status,
            ClientScheduledStatus.ERROR)
        self.assertEqual(self.stop_client.status, Client.STOPNOCONTACT)

    def test_command_process_scheduled_status_idle(self):
        ClientScheduledStatusFactory.create_batch(
            10,
            change_date=date.today(),
            operation_status=ClientScheduledStatus.PROCESSED)
        out = StringIO()
        call_command('processscheduledstatuschange', stdout=out)
        self.assertNotIn('status updated', out.getvalue())

    def test_command_process_scheduled_status(self):
        scheduled_change = ClientScheduledStatusFactory(
            client=self.active_client,
            change_date=date.today(),
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED
        )
        out = StringIO()
        call_command('processscheduledstatuschange', stdout=out)
        with translation.override('en'):
            self.assertIn('client «{}» status updated from {} to {}'.format(
                self.active_client.member,
                scheduled_change.get_status_from_display(),
                scheduled_change.get_status_to_display()
            ), out.getvalue())
        # Reload
        scheduled_change = ClientScheduledStatus.objects.get(
            id=scheduled_change.id)
        self.assertEqual(
            scheduled_change.operation_status,
            ClientScheduledStatus.PROCESSED)

    def test_form_save_bypassed(self):
        form = ClientScheduledStatusForm()
        with self.assertRaises(NotImplementedError):
            form.save()

    def test_form_save_scheduled_statuses_invalid_data(self):
        form = ClientScheduledStatusForm(initial={})
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save_scheduled_statuses()

    def test_form_save_scheduled_statuses_process_immediately(self):
        test_client = ClientFactory(status=Client.ACTIVE)
        form = ClientScheduledStatusForm({
            'client': test_client.pk,
            'status_from': Client.ACTIVE,
            'status_to': Client.PAUSED,
            'change_date': date.today(),
            'end_date': date.today()
        })
        self.assertTrue(form.is_valid())
        form.save_scheduled_statuses()
        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client,
            operation_status=ClientScheduledStatus.PROCESSED).count(), 2)

    def test_view_client_status_update_empty_dates(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')
        data = {
            'client': self.active_client.id,
            'status_from': self.active_client.status,
            'status_to': Client.PAUSED,
            'reason': '',
        }
        response = self.client.post(
            reverse_lazy('member:clientStatusScheduler',
                         kwargs={'pk': self.active_client.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )
        self.assertIn(
            ugettext('This field is required.').encode(response.charset),
            response.content
        )

    def test_view_client_status_update_future_date(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')
        data = {
            'client': self.active_client.id,
            'status_from': self.active_client.status,
            'status_to': Client.PAUSED,
            'reason': 'Holidays',
            'change_date': '2018-09-23',
            'end_date': '2018-10-02',
        }
        response = self.client.post(
            reverse_lazy('member:clientStatusScheduler',
                         kwargs={'pk': self.active_client.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )
        client = Client.objects.get(pk=self.active_client.id)
        scheduled_change_start = ClientScheduledStatus.objects.get(
            client=client.id, change_date='2018-09-23')
        scheduled_change_end = ClientScheduledStatus.objects.get(
            client=client.id, change_date='2018-10-02')
        self.assertEqual(scheduled_change_start.operation_status,
                         ClientScheduledStatus.TOBEPROCESSED)
        self.assertEqual(scheduled_change_start.status_from,
                         self.active_client.status)
        self.assertEqual(scheduled_change_start.status_to, Client.PAUSED)
        self.assertEqual(scheduled_change_start.reason, 'Holidays')
        self.assertEqual(
            scheduled_change_start.get_pair, scheduled_change_end
        )
        self.assertEqual(scheduled_change_end.operation_status,
                         ClientScheduledStatus.TOBEPROCESSED)
        self.assertEqual(scheduled_change_end.status_from, Client.PAUSED)
        self.assertEqual(scheduled_change_end.status_to,
                         self.active_client.status)
        self.assertEqual(scheduled_change_end.reason, 'Holidays')
        self.assertEqual(
            scheduled_change_end.get_pair, scheduled_change_start
        )

    def test_view_client_status_update_no_end_date(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')
        data = {
            'client': self.active_client.id,
            'status_from': self.active_client.status,
            'status_to': Client.STOPCONTACT,
            'reason': 'Holidays',
            'change_date': '2019-09-23',
            'end_date': '',
        }
        response = self.client.post(
            reverse_lazy('member:clientStatusScheduler',
                         kwargs={'pk': self.active_client.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True,
        )
        client = Client.objects.get(pk=self.active_client.id)
        scheduled_change = ClientScheduledStatus.objects.get(
            client=client.id)
        self.assertEqual(scheduled_change.operation_status,
                         ClientScheduledStatus.TOBEPROCESSED)
        self.assertEqual(scheduled_change.status_from,
                         self.active_client.status)
        self.assertEqual(scheduled_change.status_to, Client.STOPCONTACT)
        self.assertEqual(scheduled_change.reason, 'Holidays')
        self.assertEqual(scheduled_change.get_pair, None)

    def test_view_client_status_update_to_by_processed_immediately(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')
        data = {
            'client': self.active_client.id,
            'status_from': self.active_client.status,
            'status_to': Client.STOPCONTACT,
            'reason': 'Holidays',
            # set today to be processed immediately
            'change_date': date.today().isoformat(),
            'end_date': '',
        }
        self.client.post(
            reverse_lazy('member:clientStatusScheduler',
                         kwargs={'pk': self.active_client.id}),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True,
        )
        client = Client.objects.get(pk=self.active_client.id)
        scheduled_change = ClientScheduledStatus.objects.get(
            client=client.id
        )
        self.assertEqual(
            scheduled_change.operation_status,
            ClientScheduledStatus.PROCESSED
        )
        self.assertEqual(scheduled_change.status_to, Client.STOPCONTACT)
        self.assertEqual(client.status, Client.STOPCONTACT)
        self.assertEqual(scheduled_change.reason, 'Holidays')
        self.assertEqual(scheduled_change.get_pair, None)

    def test_view_client_status_delete_without_pair(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')
        self.client.post(
            reverse_lazy(
                'member:clientStatusScheduler',
                kwargs={'pk': self.active_client.id}
            ),
            {
                'client': self.active_client.id,
                'status_from': self.active_client.status,
                'status_to': Client.STOPCONTACT,
                'reason': 'Holidays',
                'change_date': '2019-09-23',
                'end_date': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True,
        )

        self.assertEqual(1, ClientScheduledStatus.objects.count())

        self.client.post(
            reverse_lazy(
                'member:delete_status',
                kwargs={'pk': ClientScheduledStatus.objects.first().id}
            ),
        )

        self.assertEqual(0, ClientScheduledStatus.objects.count())

    def test_view_client_status_delete_with_not_logged_user(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')
        self.client.post(
            reverse_lazy(
                'member:clientStatusScheduler',
                kwargs={'pk': self.active_client.id}
            ),
            {
                'client': self.active_client.id,
                'status_from': self.active_client.status,
                'status_to': Client.PAUSED,
                'reason': 'Holidays',
                'change_date': '2018-09-23',
                'end_date': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )

        self.assertEqual(1, ClientScheduledStatus.objects.count())

        self.client.logout()

        client_status_base = ClientScheduledStatus.objects.first()
        response = self.client.post(
            reverse_lazy(
                'member:delete_status',
                kwargs={'pk': client_status_base.id}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_view_client_status_delete_with_not_admin_user(self):
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='user1234'
        )
        self.client.login(username=admin.username, password='test1234')
        self.client.post(
            reverse_lazy(
                'member:clientStatusScheduler',
                kwargs={'pk': self.active_client.id}
            ),
            {
                'client': self.active_client.id,
                'status_from': self.active_client.status,
                'status_to': Client.PAUSED,
                'reason': 'Holidays',
                'change_date': '2018-09-23',
                'end_date': '2018-10-02',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )

        self.assertEqual(2, ClientScheduledStatus.objects.count())

        self.client.logout()
        self.client.login(username=user.username, password='user1234')

        client_status_base = ClientScheduledStatus.objects.first()
        response = self.client.post(
            reverse_lazy(
                'member:delete_status',
                kwargs={'pk': client_status_base.id}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_view_reschedule_pair_valid(self):
        """
        A valid pair is retrieved (GET) and replaced (POST) together.
        """
        test_client = ClientFactory(status=Client.ACTIVE)
        c1 = ClientScheduledStatusFactory(
            client=test_client,
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
            change_date=date.today() + timedelta(days=1),
            operation_status=ClientScheduledStatus.TOBEPROCESSED)
        c2 = ClientScheduledStatusFactory(
            client=test_client,
            status_from=Client.PAUSED,
            status_to=Client.ACTIVE,
            change_date=date.today() + timedelta(days=7),
            operation_status=ClientScheduledStatus.TOBEPROCESSED,
            pair=c1)

        self.force_login()

        # GET
        response = self.client.get(
            reverse(
                'member:clientStatusSchedulerReschedule',
                kwargs={
                    'pk': test_client.pk,
                    'scheduled_status_1_pk': c1.pk,
                    'scheduled_status_2_pk': c2.pk,
                }
            )
        )
        self.assertEqual(response.status_code, 200)
        cf = response.context['form'].initial
        self.assertEqual(cf['client'], str(test_client.pk))
        self.assertEqual(cf['status_from'], Client.ACTIVE)
        self.assertEqual(cf['status_to'], Client.PAUSED)
        self.assertEqual(cf['change_date'], date.today() + timedelta(days=1))
        self.assertEqual(cf['end_date'], date.today() + timedelta(days=7))

        # POST
        response = self.client.post(
            reverse(
                'member:clientStatusSchedulerReschedule',
                kwargs={
                    'pk': test_client.pk,
                    'scheduled_status_1_pk': c1.pk,
                    'scheduled_status_2_pk': c2.pk,
                }
            ), {
                'client': str(test_client.pk),
                'status_from': Client.ACTIVE,
                'status_to': Client.STOPCONTACT,
                'reason': 'some reason',
                'change_date': date.today() + timedelta(days=2),
                'end_date': date.today() + timedelta(days=12)
            }
        )
        # Successful
        self.assertRedirects(response, reverse(
            'member:client_information', kwargs={'pk': test_client.pk}))

        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client).count(), 2)
        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client,
            status_from=Client.ACTIVE,
            status_to=Client.STOPCONTACT,
            change_date=date.today() + timedelta(days=2)
        ).count(), 1)
        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client,
            status_from=Client.STOPCONTACT,
            status_to=Client.ACTIVE,
            change_date=date.today() + timedelta(days=12)
        ).count(), 1)

    def test_view_reschedule_pair_invalid(self):
        """
        In an invalid pair, only the first ClientScheduledStatus instance
        is retrieved (GET) and replaced (POST).
        """
        test_client = ClientFactory(status=Client.ACTIVE)
        c1 = ClientScheduledStatusFactory(
            client=test_client,
            status_from=Client.ACTIVE,
            status_to=Client.PAUSED,
            change_date=date.today() + timedelta(days=1),
            operation_status=ClientScheduledStatus.TOBEPROCESSED)
        c2 = ClientScheduledStatusFactory(
            client=test_client,
            status_from=Client.PAUSED,
            status_to=Client.ACTIVE,
            reason='invalid pair',
            change_date=date.today() + timedelta(days=7),
            operation_status=ClientScheduledStatus.TOBEPROCESSED,
            pair=ClientScheduledStatusFactory(client=ClientFactory()))

        self.force_login()

        # GET
        response = self.client.get(
            reverse(
                'member:clientStatusSchedulerReschedule',
                kwargs={
                    'pk': test_client.pk,
                    'scheduled_status_1_pk': c1.pk,
                    'scheduled_status_2_pk': c2.pk,
                }
            )
        )
        self.assertEqual(response.status_code, 200)
        cf = response.context['form'].initial
        self.assertEqual(cf['client'], str(test_client.pk))
        self.assertEqual(cf['status_from'], Client.ACTIVE)
        self.assertEqual(cf['status_to'], Client.PAUSED)
        self.assertEqual(cf['change_date'], date.today() + timedelta(days=1))
        self.assertEqual(cf['end_date'], None)

        # POST
        response = self.client.post(
            reverse(
                'member:clientStatusSchedulerReschedule',
                kwargs={
                    'pk': test_client.pk,
                    'scheduled_status_1_pk': c1.pk,
                    'scheduled_status_2_pk': c2.pk,
                }
            ), {
                'client': str(test_client.pk),
                'status_from': Client.ACTIVE,
                'status_to': Client.STOPCONTACT,
                'reason': 'some reason',
                'change_date': date.today() + timedelta(days=2),
                'end_date': date.today() + timedelta(days=12)
            }
        )
        # Successful
        self.assertRedirects(response, reverse(
            'member:client_information', kwargs={'pk': test_client.pk}))

        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client).count(), 3)
        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client,
            status_from=Client.ACTIVE,
            status_to=Client.STOPCONTACT,
            change_date=date.today() + timedelta(days=2)
        ).count(), 1)
        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client,
            status_from=Client.STOPCONTACT,
            status_to=Client.ACTIVE,
            change_date=date.today() + timedelta(days=12)
        ).count(), 1)
        self.assertEqual(ClientScheduledStatus.objects.filter(
            client=test_client,
            reason='invalid pair'
        ).count(), 1)


class ClientUpdateTestCase(TestCase):

    fixtures = ['routes.json']

    def login_as_admin(self):
        """
        Login as administrator.
        """
        admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test1234'
        )
        self.client.login(username=admin.username, password='test1234')

    def test_redirect_to_next(self):
        """
        If "?next" exists in URL parameter, the 302 redirect should
        point to this URL upon successful form submission.
        """
        client = ClientFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data['firstname'] = 'John'
        data['lastname'] = 'Doe'
        data['birthdate'] = '1923-03-21'
        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        response = self.client.post(
            reverse(
                'member:member_update_basic_information',
                kwargs={
                    'pk': client.id
                }
            ) + '?next=/fake/any_url',
            data,
            follow=True
        )

        self.assertRedirects(
            response, '/fake/any_url',
            status_code=302, target_status_code=404
        )


class ClientUpdateBasicInformation(ClientUpdateTestCase):

    def test_form_validation(self):
        """
        Test validation form.
        """
        client = ClientFactory()
        form_data = {
            'firstname': 'John'
        }
        form = ClientBasicInformation(data=form_data)
        self.assertFalse(form.is_valid())
        form = ClientBasicInformation(data=load_initial_data(client))
        self.assertTrue(form.is_valid())

    def test_update_basic_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data['firstname'] = 'John'
        data['lastname'] = 'Doe'
        data['birthdate'] = '1923-03-21'
        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_basic_information',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        # Test that values have been updated
        self.assertEqual(str(client), 'John Doe')
        self.assertEqual(client.birthdate, date(1923, 3, 21))
        # Test that old values are still there
        self.assertEqual(client.alert, data.get('alert'))
        self.assertEqual(client.gender, data.get('gender'))
        self.assertEqual(client.language, data.get('language'))


class ClientUpdateAddressInformation(ClientUpdateTestCase):

    def test_form_validation(self):
        """
        Test validation form.
        """
        client = ClientFactory()
        form_data = {
            'street': '111 rue Roy'
        }
        form = ClientAddressInformation(data=form_data)
        self.assertFalse(form.is_valid())
        form = ClientAddressInformation(data=load_initial_data(client))
        self.assertTrue(form.is_valid())

    def test_update_address_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data['street'] = '111 rue Roy Est'
        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_address_information',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertEqual(client.member.address.street, '111 rue Roy Est')
        self.assertEqual(client.member.address.city, data.get('city'))
        self.assertEqual(client.route.id, data.get('route'))
        self.assertEqual(client.delivery_note, data.get('delivery_note'))
        self.assertEqual(Decimal(client.member.address.latitude),
                         Decimal(data.get('latitude')))
        self.assertEqual(Decimal(str(client.member.address.longitude)),
                         Decimal(data.get('longitude')))


class ClientUpdatePaymentInformationTestCase(ClientUpdateTestCase):

    def test_form_validation(self):
        """
        Test validation form.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        data.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': None,
            'postal_code': None,
            'member': '[0] Not Valid'.format(
                client.billing_member.id,
                client.billing_member.firstname,
                client.billing_member.lastname
            ),
            'same_as_client': False,
            'billing_payment_type': 'cheque',
            'facturation': 'default',
        })
        form = ClientPaymentInformation(data=data)
        self.assertFalse(form.is_valid())
        data.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': None,
            'postal_code': None,
            'member': '[{}] {} {}'.format(
                client.member.id,
                client.member.firstname,
                client.member.lastname
            ),
            'same_as_client': True,
            'billing_payment_type': 'eft',
            'facturation': 'default',
        })
        form = ClientPaymentInformation(data=data)

        self.assertTrue(form.is_valid())

    def test_update_payment_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        payment = MemberFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': '',
            'postal_code': 'H2R2N3',
            'member': '[{}] {} {}'.format(
                payment.id,
                payment.firstname,
                payment.lastname
            ),
            'same_as_client': False,
            'billing_payment_type': '',
            'facturation': 'default',
        })

        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_payment_information',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )
        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertEqual(client.billing_member.id, payment.id)
        self.assertEqual(client.billing_member.firstname, payment.firstname)
        self.assertEqual(client.billing_member.lastname, payment.lastname)


class ClientUpdateDietaryRestrictionTestCase(ClientUpdateTestCase):

    def test_form_validation(self):
        """
        Test validation form.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'status': True if client.status == Client.ACTIVE else False,
            'delivery_type': client.delivery_type,
            'meals_schedule': ['monday']
        })
        for day in data['meals_schedule']:
            data['size_{}'.format(day)] = 'R'
            for component, _ in COMPONENT_GROUP_CHOICES:
                name = "{}_{}_quantity".format(component, day)
                data[name] = 1

        form = ClientRestrictionsInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_update_dietary_restriction(self):
        """
        Test the update basic information form.
        """
        Option.objects.create(name='meals_schedule')
        client = ClientFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Make sure the status stays unchanged
        status = client.status
        # Update some data
        data.update({
            'status': "A",
            'delivery_type': "O",
            'meals_schedule': ["monday"],
        })
        for day in data['meals_schedule']:
            data['size_{}'.format(day)] = 'R'
            for component, _ in COMPONENT_GROUP_CHOICES:
                name = "{}_{}_quantity".format(component, day)
                data[name] = 1

        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_update_dietary_restriction',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertEqual(client.status, status)
        self.assertEqual(client.delivery_type, "O")

    def test_meal_default_should_be_set_for_scheduled_delivery_days(self):
        """
        On delivery days, at least one of the quantities should be set for an
        ongoing client.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'status': True if client.status == Client.ACTIVE else False,
            'delivery_type': 'O',
            'meals_schedule': ['monday']
        })
        for day in ['tuesday', 'sunday']:
            data['size_{}'.format(day)] = 'R'
            for component, _ in COMPONENT_GROUP_CHOICES:
                name = "{}_{}_quantity".format(component, day)
                data[name] = 1

        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data['compote_monday_quantity'] = 1
        form = ClientRestrictionsInformation(data=data)
        self.assertTrue(form.is_valid())

        data['compote_monday_quantity'] = 0
        data['main_dish_monday_quantity'] = 1
        data['size_monday'] = 'L'
        form = ClientRestrictionsInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_meal_default_should_not_be_enforced_for_episodic_client(self):
        """
        For episodic client, the restrictions above should not be applied.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'status': True if client.status == Client.ACTIVE else False,
            'delivery_type': 'E',
            'meals_schedule': ['monday']
        })
        for day in ['tuesday', 'sunday']:
            data['size_{}'.format(day)] = 'R'
            for component, _ in COMPONENT_GROUP_CHOICES:
                name = "{}_{}_quantity".format(component, day)
                data[name] = 1

        form = ClientRestrictionsInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_main_dish_enforces_size(self):
        """
        Whenever the quantity of main dish is set, the size should also be set.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'status': True if client.status == Client.ACTIVE else False,
            'delivery_type': 'E',
            'meals_schedule': []
        })
        form = ClientRestrictionsInformation(data=data)
        self.assertTrue(form.is_valid())

        data['main_dish_tuesday_quantity'] = 1
        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data['size_wednesday'] = 'L'
        form = ClientRestrictionsInformation(data=data)
        self.assertFalse(form.is_valid())

        data['size_tuesday'] = 'R'
        form = ClientRestrictionsInformation(data=data)
        self.assertTrue(form.is_valid())


class ClientUpdateRelationshipsTestCase(ClientUpdateTestCase):

    def test_form_validation_existing_member(self):
        """
        Test validation form.
        """
        relationship = RelationshipFactory()
        client = relationship.client
        data = load_initial_data(client)
        data.update({
            'firstname': None,
            'lastname': None,
            'member': '[0] Not Valid',
        })
        form = ClientRelationshipInformation(data=data)
        self.assertFalse(form.is_valid())
        member = relationship.member
        data.update({
            'firstname': None,
            'lastname': None,
            'member': '[{}] {} {}'.format(
                member.id,
                member.firstname,
                member.lastname
            ),
            'nature': 'friend',
        })

        form = ClientRelationshipInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_form_validation_new_relationship_member(self):
        """
        Test validation form.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        data.update({
            'firstname': None,
            'lastname': None,
            'member': None,
            'type': [],
            'nature': 'friend'
        })
        form = ClientRelationshipInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'firstname': 'test',
            'lastname': 'test',
        })
        form = ClientRelationshipInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'cell_phone': '514-122-3333'
        })
        form = ClientRelationshipInformation(data=data)
        self.assertTrue(form.is_valid())

        data['cell_phone'] = None
        data.update({
            'work_phone': '514-122-3333'
        })
        form = ClientRelationshipInformation(data=data)
        self.assertTrue(form.is_valid())

        data['work_phone'] = None
        data.update({
            'email': 'invalid email'
        })
        form = ClientRelationshipInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'email': 'valid@email.com'
        })
        form = ClientRelationshipInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_update_relationship_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        member = MemberFactory()  # Another member
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data.update({
            "relationships-TOTAL_FORMS": "1",
            "relationships-INITIAL_FORMS": "1",
            "relationships-MIN_NUM_FORMS": "0",
            "relationships-MAX_NUM_FORMS": "1000",
            "relationships-0-firstname": None,
            "relationships-0-lastname": None,
            'relationships-0-member': '[{}] {} {}'.format(
                member.id,
                member.firstname,
                member.lastname
            ),
            'relationships-0-type': [],
            'relationships-0-nature': 'friend'
        })

        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_relationships',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertIn(
            member.id,
            [c.member.pk for c in client.relationship_set.all()]
        )
        self.assertIn(
            member.firstname,
            [c.member.firstname for c in client.relationship_set.all()]
        )
        self.assertIn(
            member.lastname,
            [c.member.lastname for c in client.relationship_set.all()]
        )


class RedirectAnonymousUserTestCase(SousChefTestMixin, TestCase):

    fixtures = ['routes.json']

    def test_anonymous_user_gets_redirect_to_login_page(self):
        check = self.assertRedirectsWithAllMethods
        check(reverse('member:member_step'))
        check(reverse('member:member_step', kwargs={
            'step': 'basic_information'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'address_information'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'relationships'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'payment_information'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'dietary_restriction'
        }))
        check(reverse('member:list'))
        check(reverse('member:search'))
        check(reverse('member:view', kwargs={'pk': 1}))
        check(reverse('member:list_orders', kwargs={'pk': 1}))
        check(reverse('member:client_information', kwargs={'pk': 1}))
        check(reverse('member:client_payment', kwargs={'pk': 1}))
        check(reverse('member:client_allergies', kwargs={'pk': 1}))
        check(reverse('member:client_notes', kwargs={'pk': 1}))
        check(reverse('member:geolocateAddress'))
        check(reverse('member:client_status', kwargs={'pk': 1}))
        check(reverse('member:clientStatusScheduler', kwargs={'pk': 1}))
        check(reverse('member:restriction_delete', kwargs={'pk': 1}))
        check(reverse('member:client_option_delete', kwargs={'pk': 1}))
        check(reverse('member:ingredient_to_avoid_delete', kwargs={'pk': 1}))
        check(reverse('member:component_to_avoid_delete', kwargs={'pk': 1}))
        check(reverse('member:member_update_basic_information', kwargs={
            'pk': 1
        }))
        check(reverse('member:member_update_address_information', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_payment_information', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_dietary_restriction', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_relationships', kwargs={
            'pk': 1
        }))

        check(reverse('member:route_list'))
        check(reverse('member:route_detail', kwargs={
            'pk': 1
        }))
        check(reverse('member:route_edit', kwargs={
            'pk': 1
        }))
        check(reverse('member:route_get_optimised_sequence', kwargs={
            'pk': 1
        }))
        check(reverse('member:delivery_history_detail', kwargs={
            'route_pk': 1,
            'date': '2000-01-01'
        }))


class ClientListViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('member:list')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('member:list')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientInfoViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_information', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_information', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientPaymentViewViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_payment', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_payment', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientAllergiesViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_allergies', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_allergies', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientStatusViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_status', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_status', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientNotesViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_notes', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_notes', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientOrderListTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:list_orders', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:list_orders', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientUpdateBasicInformationViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_basic_information',
            kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_basic_information',
            kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientUpdateAddressInformationViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_address_information',
            kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_address_information',
            kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientUpdatePaymentInformationViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_payment_information',
            kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_payment_information',
            kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientUpdateDietaryRestrictionViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_dietary_restriction',
            kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        Option.objects.create(name='meals_schedule')
        client = ClientFactory()
        url = reverse(
            'member:member_update_dietary_restriction',
            kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientUpdateRelationshipsViewTestCase(
        SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_relationships',
            kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse(
            'member:member_update_relationships',
            kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class SearchMembersViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('member:search')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('member:search')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientStatusSchedulerViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:clientStatusScheduler', kwargs={'pk': client.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:clientStatusScheduler', kwargs={'pk': client.id})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class DeleteRestrictionViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        restricted_item = Restricted_item.objects.create(
            name='pork', restricted_item_group='meat')
        restriction = Restriction.objects.create(
            client=client, restricted_item=restricted_item)
        url = reverse(
            'member:restriction_delete', kwargs={'pk': restriction.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        restricted_item = Restricted_item.objects.create(
            name='pork', restricted_item_group='meat')
        restriction = Restriction.objects.create(
            client=client, restricted_item=restricted_item)
        url = reverse(
            'member:restriction_delete', kwargs={'pk': restriction.id})
        # Run
        response = self.client.post(url, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)


class DeleteClientOptionViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        option = Option.objects.create(name='test')
        coption = Client_option.objects.create(client=client, option=option)
        url = reverse('member:client_option_delete', kwargs={'pk': coption.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        option = Option.objects.create(name='test')
        coption = Client_option.objects.create(client=client, option=option)
        url = reverse('member:client_option_delete', kwargs={'pk': coption.id})
        # Run
        response = self.client.post(url, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)


class DeleteIngredientToAvoidViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        ingredient = Ingredient.objects.create(name='ground pork')
        avoid_ing = Client_avoid_ingredient.objects.create(
            client=client, ingredient=ingredient)
        url = reverse(
            'member:ingredient_to_avoid_delete', kwargs={'pk': avoid_ing.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        ingredient = Ingredient.objects.create(name='ground pork')
        avoid_ing = Client_avoid_ingredient.objects.create(
            client=client, ingredient=ingredient)
        url = reverse(
            'member:ingredient_to_avoid_delete', kwargs={'pk': avoid_ing.id})
        # Run
        response = self.client.post(url, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)


class DeleteComponentToAvoidViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        component = Component.objects.create(
            name='ginger pork', component_group='main dish')
        avoid_component = Client_avoid_component.objects.create(
            client=client, component=component)
        url = reverse(
            'member:component_to_avoid_delete',
            kwargs={'pk': avoid_component.id})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        component = Component.objects.create(
            name='ginger pork', component_group='main dish')
        avoid_component = Client_avoid_component.objects.create(
            client=client, component=component)
        url = reverse(
            'member:component_to_avoid_delete',
            kwargs={'pk': avoid_component.id})
        # Run
        response = self.client.post(url, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)


class TestMigrationApply0026(TestMigrations):
    migrate_from = '0025_route_vehicle'
    migrate_to = '0026_change_to_emergency_contacts'

    def setUpBeforeMigration(self, apps):
        Member = apps.get_model('member', 'Member')
        Client = apps.get_model('member', 'Client')

        member1 = Member.objects.create(
            firstname="HasContact",
            lastname="HasContactRelationship"
        )
        member2 = Member.objects.create(
            firstname="HasContact",
            lastname="NoContactRelationship"
        )
        member3 = Member.objects.create(
            firstname="NoContact",
            lastname="HasContactRelationship"
        )
        member4 = Member.objects.create(
            firstname="NoContact",
            lastname="NoContactRelationship"
        )
        emgc_member = Member.objects.create(
            firstname="John",
            lastname="Doe"
        )
        client1 = Client.objects.create(
            billing_member=member1,
            member=member1,
            # Important fields
            emergency_contact=emgc_member,
            emergency_contact_relationship='friend'
        )
        client2 = Client.objects.create(
            billing_member=member2,
            member=member2,
            # Important fields
            emergency_contact=emgc_member,
            emergency_contact_relationship=None
        )
        client3 = Client.objects.create(
            billing_member=member3,
            member=member3,
            # Important fields
            emergency_contact=None,
            emergency_contact_relationship='friend'
        )
        client4 = Client.objects.create(
            billing_member=member4,
            member=member4,
            # Important fields
            emergency_contact=None,
            emergency_contact_relationship=None
        )

    def test_emergency_contact_migrated(self):
        Member = self.apps.get_model('member', 'Member')
        Client = self.apps.get_model('member', 'Client')
        EmergencyContact = self.apps.get_model('member', 'EmergencyContact')

        client1 = Client.objects.get(
            member__firstname="HasContact",
            member__lastname="HasContactRelationship"
        )
        client2 = Client.objects.get(
            member__firstname="HasContact",
            member__lastname="NoContactRelationship"
        )
        client3 = Client.objects.get(
            member__firstname="NoContact",
            member__lastname="HasContactRelationship"
        )
        client4 = Client.objects.get(
            member__firstname="NoContact",
            member__lastname="NoContactRelationship"
        )

        self.assertEqual(client1.emergency_contacts.count(), 1)
        self.assertEqual(client2.emergency_contacts.count(), 1)
        self.assertEqual(client3.emergency_contacts.count(), 0)
        self.assertEqual(client4.emergency_contacts.count(), 0)

        emgc_member = Member.objects.get(
            firstname="John",
            lastname="Doe"
        )

        emgc1 = client1.emergency_contacts.first()
        self.assertEqual(emgc1, emgc_member)
        ec1 = EmergencyContact.objects.get(client=client1, member=emgc1)
        self.assertEqual(ec1.relationship, 'friend')

        emgc2 = client2.emergency_contacts.first()
        self.assertEqual(emgc2, emgc_member)
        ec2 = EmergencyContact.objects.get(client=client2, member=emgc2)
        self.assertEqual(ec2.relationship, None)


class TestMigrationUnapply0026(TestMigrations):
    migrate_from = '0026_change_to_emergency_contacts'
    migrate_to = '0025_route_vehicle'

    def setUpBeforeMigration(self, apps):
        Member = apps.get_model('member', 'Member')
        Client = apps.get_model('member', 'Client')
        EmergencyContact = apps.get_model('member', 'EmergencyContact')

        member0 = Member.objects.create(
            firstname="No",
            lastname="EmergencyContact"
        )
        member1 = Member.objects.create(
            firstname="One",
            lastname="EmergencyContact"
        )
        member2 = Member.objects.create(
            firstname="Two",
            lastname="EmergencyContact"
        )
        emgc_member1 = Member.objects.create(
            firstname="John",
            lastname="Doe"
        )
        emgc_member2 = Member.objects.create(
            firstname="Andy",
            lastname="Lee"
        )
        client0 = Client.objects.create(
            billing_member=member0,
            member=member0,
        )
        client1 = Client.objects.create(
            billing_member=member1,
            member=member1,
        )
        EmergencyContact.objects.create(
            client=client1,
            member=emgc_member1,
            relationship='friend'
        )
        client2 = Client.objects.create(
            billing_member=member2,
            member=member2,
        )
        EmergencyContact.objects.create(
            client=client2,
            member=emgc_member1,
            relationship='friend1'
        )
        EmergencyContact.objects.create(
            client=client2,
            member=emgc_member2,
            relationship='friend2'
        )

    def test_emergency_contact_migrated(self):
        Member = self.apps.get_model('member', 'Member')
        Client = self.apps.get_model('member', 'Client')

        client0 = Client.objects.get(
            member__firstname="No",
            member__lastname="EmergencyContact"
        )
        client1 = Client.objects.get(
            member__firstname="One",
            member__lastname="EmergencyContact"
        )
        client2 = Client.objects.get(
            member__firstname="Two",
            member__lastname="EmergencyContact"
        )
        emgc_member1 = Member.objects.get(
            firstname="John",
            lastname="Doe"
        )
        emgc_member2 = Member.objects.get(
            firstname="Andy",
            lastname="Lee"
        )

        self.assertEqual(client0.emergency_contact, None)
        self.assertEqual(client0.emergency_contact_relationship, None)

        self.assertEqual(client1.emergency_contact, emgc_member1)
        self.assertEqual(client1.emergency_contact_relationship, 'friend')

        self.assertIn(client2.emergency_contact, [emgc_member1, emgc_member2])
        if client2.emergency_contact == emgc_member1:
            self.assertIn(client2.emergency_contact_relationship, 'friend1')
        else:
            self.assertIn(client2.emergency_contact_relationship, 'friend2')


class TestMigrationApply0029(TestMigrations):
    """
    Refs #704.
    """
    migrate_from = '0028_change_linked_scheduled_status_relationship'
    migrate_to = '0029_member_address_fk_to_1to1'

    def setUpBeforeMigration(self, apps):
        Member = apps.get_model('member', 'Member')
        Address = apps.get_model('member', 'Address')

        addr0 = Address.objects.create(
            street="no member",
            city="-",
            postal_code="-"
        )
        addr1 = Address.objects.create(
            street="one member",
            city="-",
            postal_code="-"
        )
        addr2 = Address.objects.create(
            street="two members",
            city="-",
            postal_code="-"
        )
        addr3 = Address.objects.create(
            street="three members",
            city="-",
            postal_code="-"
        )

        member1 = Member.objects.create(
            firstname="1",
            lastname="-",
            address=addr1
        )
        member2a = Member.objects.create(
            firstname="2",
            lastname="a",
            address=addr2
        )
        member2b = Member.objects.create(
            firstname="2",
            lastname="b",
            address=addr2
        )
        member3a = Member.objects.create(
            firstname="3",
            lastname="a",
            address=addr3
        )
        member3b = Member.objects.create(
            firstname="3",
            lastname="b",
            address=addr3
        )
        member3c = Member.objects.create(
            firstname="3",
            lastname="c",
            address=addr3
        )
        member_no_addr = Member.objects.create(
            firstname="No",
            lastname="Address",
            address=None
        )

        self.data = {
            'addr0_pk': addr0.pk,
            'addr1_pk': addr1.pk,
            'addr2_pk': addr2.pk,
            'addr3_pk': addr3.pk,
        }

    def test_address_objects_separated(self):
        Member = self.apps.get_model('member', 'Member')
        Address = self.apps.get_model('member', 'Address')

        member1 = Member.objects.get(
            firstname="1",
            lastname="-"
        )
        member2a = Member.objects.get(
            firstname="2",
            lastname="a"
        )
        member2b = Member.objects.get(
            firstname="2",
            lastname="b"
        )
        member3a = Member.objects.get(
            firstname="3",
            lastname="a"
        )
        member3b = Member.objects.get(
            firstname="3",
            lastname="b"
        )
        member3c = Member.objects.get(
            firstname="3",
            lastname="c"
        )

        # Test addr0: there should be no changes.
        self.assertEqual(
            Address.objects.filter(pk=self.data['addr0_pk']).count(),
            1
        )
        addr0 = Address.objects.get(pk=self.data['addr0_pk'])
        self.assertEqual(addr0.street, "no member")

        # Test addr1: there should be no changes.
        self.assertEqual(
            Address.objects.filter(pk=self.data['addr1_pk']).count(),
            1
        )
        addr1 = Address.objects.get(pk=self.data['addr1_pk'])
        self.assertEqual(addr1.street, "one member")
        self.assertEqual(member1.address.pk, addr1.pk)

        # Test addr2: it should be split into 2 instances.
        # But we still have the original instance.
        self.assertEqual(
            Address.objects.filter(street="two members").count(),
            2
        )
        self.assertEqual(
            Address.objects.filter(pk=self.data['addr2_pk']).count(),
            1
        )
        self.assertEqual(member2a.address.street, "two members")
        self.assertEqual(member2b.address.street, "two members")

        # Test addr3: it should be split into 3 instances.
        # But we still have the original instance.
        self.assertEqual(
            Address.objects.filter(street="three members").count(),
            3
        )
        self.assertEqual(
            Address.objects.filter(pk=self.data['addr3_pk']).count(),
            1
        )
        self.assertEqual(member3a.address.street, "three members")
        self.assertEqual(member3b.address.street, "three members")
        self.assertEqual(member3c.address.street, "three members")

        # Test member without address
        member_no_addr = Member.objects.get(
            firstname="No",
            lastname="Address"
        )
        self.assertEqual(member_no_addr.address, None)


class RouteListViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('member:route_list')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('member:route_list')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class RouteDetailViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('member:route_detail', kwargs={'pk': 1})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('member:route_detail', kwargs={'pk': 1})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_parsing_client_id_sequence(self):
        """
        Unorganised clients should be placed at the end.
        Invalid clients should be ignored.
        """
        route = RouteFactory()
        clients_on_route = ClientFactory.create_batch(
            10,
            route=route
        )
        clients_organised = (
            clients_on_route[1], clients_on_route[3],
            clients_on_route[5], clients_on_route[7],
            clients_on_route[9]
        )
        clients_unorganised = (
            clients_on_route[0], clients_on_route[2],
            clients_on_route[4], clients_on_route[6],
            clients_on_route[8]
        )
        route.client_id_sequence = [
            "N/A", clients_organised[0].pk,
            299999, clients_organised[1].pk,
            "INVALID", clients_organised[2].pk,
            "[DELETED]", clients_organised[3].pk,
            599999, clients_organised[4].pk,
        ]
        route.save()

        self.force_login()
        url = reverse('member:route_detail', kwargs={'pk': route.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        clients_on_route = response.context['clients_on_route']
        self.assertEqual(len(clients_on_route), 10)
        self.assertEqual(clients_on_route[0].pk, clients_organised[0].pk)
        self.assertEqual(clients_on_route[1].pk, clients_organised[1].pk)
        self.assertEqual(clients_on_route[2].pk, clients_organised[2].pk)
        self.assertEqual(clients_on_route[3].pk, clients_organised[3].pk)
        self.assertEqual(clients_on_route[4].pk, clients_organised[4].pk)
        self.assertTrue(clients_on_route[0].has_been_configured)
        self.assertTrue(clients_on_route[1].has_been_configured)
        self.assertTrue(clients_on_route[2].has_been_configured)
        self.assertTrue(clients_on_route[3].has_been_configured)
        self.assertTrue(clients_on_route[4].has_been_configured)
        self.assertEqual(
            set(map(lambda c: c.pk, clients_unorganised)),
            set(map(lambda c: c.pk, clients_on_route[5:]))
        )
        self.assertFalse(clients_on_route[5].has_been_configured)
        self.assertFalse(clients_on_route[6].has_been_configured)
        self.assertFalse(clients_on_route[7].has_been_configured)
        self.assertFalse(clients_on_route[8].has_been_configured)
        self.assertFalse(clients_on_route[9].has_been_configured)


class RouteEditViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        route = RouteFactory()
        url = reverse(
            'member:route_edit',
            kwargs={'pk': route.pk})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        route = RouteFactory()
        url = reverse(
            'member:route_edit',
            kwargs={'pk': route.pk})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_post_valid_form(self):
        route = RouteFactory()
        self.force_login()
        url = reverse(
            'member:route_edit',
            kwargs={'pk': route.pk})
        response = self.client.post(url, {
            'name': 'new name',
            'description': 'test',
            'vehicle': 'driving',
            'client_id_sequence': '[100, 110]'
        })
        self.assertRedirects(response, reverse_lazy(
            'member:route_detail', args=[route.pk]))


class RouteGetOptimisedSequenceViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('member:route_get_optimised_sequence', kwargs={'pk': 1})
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('member:route_get_optimised_sequence', kwargs={'pk': 1})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_client_numbers_should_be_the_same(self):
        # Setup data
        route = RouteFactory()
        clients = ClientFactory.create_batch(
            10,
            route=route)

        self.force_login()
        url = reverse(
            'member:route_get_optimised_sequence', kwargs={'pk': route.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        try:
            result = json.loads(response.content.decode(response.charset))
            self.assertEqual(len(result), 10)
        except (TypeError, ValueError) as e:
            self.fail("Response is not valid JSON.")


class RouteDeliveryHistoryDetailViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        r = RouteFactory()
        dh = DeliveryHistoryFactory(
            route=r,
            date=timezone.datetime.date(
                timezone.datetime(2001, 1, 1)
            )
        )
        url = reverse('member:delivery_history_detail', kwargs={
            'route_pk': r.pk,
            'date': '2001-01-01'
        })
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        r = RouteFactory()
        dh = DeliveryHistoryFactory(
            route=r,
            date=timezone.datetime.date(
                timezone.datetime(2001, 1, 1)
            )
        )
        url = reverse('member:delivery_history_detail', kwargs={
            'route_pk': r.pk,
            'date': '2001-01-01'
        })
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_parsing_client_id_sequence(self):
        """
        Should be in the order:
        (1) Delivery history sequence
        (2) Then route sequence
        (3) Then random order

        Except for the problematic ones, which means:
        (1) Invalid client ID or client doesn't exist
        (2) The client's order on that day was not found and we think the
            client is invalid on this delivery sequence.
        """
        route = RouteFactory()
        dh = DeliveryHistoryFactory(
            route=route,
            date=timezone.datetime.date(
                timezone.datetime(2001, 1, 1)
            )
        )
        clients = ClientFactory.create_batch(
            10,
            route=route,
            status=Client.ACTIVE
        )
        route.client_id_sequence = list(map(
            lambda x: clients[x].pk,
            [1, 3, 5, 7, 9, 0, 2, 4, 6, 8]
        ))
        route.save(update_fields=['client_id_sequence'])

        # We delivered clients[7, 9, 0, 2, 4, 6]:
        orders_dict = {}
        for x in [7, 9, 0, 2, 4, 6]:
            c = clients[x]
            o = OrderFactory(
                client=c,
                delivery_date=timezone.datetime.date(
                    timezone.datetime(2001, 1, 1)
                ),
                status=ORDER_STATUS_ORDERED
            )
            orders_dict[x] = o

        # We imagine to have delivered clients[5] but deleted his order.
        # We then change clients[2]'s route to make it invalid.
        clients[2].route = RouteFactory()
        clients[2].save(update_fields=['route'])

        dh.client_id_sequence = [
            "N/A",  # Invalid client ID
            clients[0].pk,
            999999,  # Client doesn't exist for sure
            clients[2].pk,  # Invalid because of route
            clients[5].pk,  # Invalid because order doesn't exist
            clients[7].pk,
            # clients[9], clients[4], clients[6] are not in this list
            # and should be placed by default seq.
        ]
        dh.save(update_fields=['client_id_sequence'])

        # The expected sequence should be:
        # [0, 7, 9, 4, 6]
        self.force_login()
        url = reverse('member:delivery_history_detail', kwargs={
            'route_pk': route.pk,
            'date': '2001-01-01'
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        clients_on_dh = response.context['clients_on_delivery_history']

        # 5 clients who had delivery
        self.assertEqual(len(clients_on_dh), 5)
        self.assertEqual(clients_on_dh[0].pk, clients[0].pk)
        self.assertEqual(clients_on_dh[1].pk, clients[7].pk)
        self.assertEqual(clients_on_dh[2].pk, clients[9].pk)
        self.assertEqual(clients_on_dh[3].pk, clients[4].pk)
        self.assertEqual(clients_on_dh[4].pk, clients[6].pk)

        # 4 invalid messages
        messages = response.context['messages']
        self.assertEqual(len(messages), 4)
        iter_messages = iter(messages)
        message0 = next(iter_messages)
        self.assertIn('N/A', message0.message)
        message1 = next(iter_messages)
        self.assertIn('999999', message1.message)
        message2 = next(iter_messages)
        self.assertIn(clients[2].member.firstname, message2.message)
        self.assertIn(clients[2].member.lastname, message2.message)
        message3 = next(iter_messages)
        self.assertIn(clients[5].member.firstname, message3.message)
        self.assertIn(clients[5].member.lastname, message3.message)

        # configured?
        self.assertTrue(clients_on_dh[0].has_been_configured)
        self.assertTrue(clients_on_dh[1].has_been_configured)
        self.assertFalse(clients_on_dh[2].has_been_configured)
        self.assertFalse(clients_on_dh[3].has_been_configured)
        self.assertFalse(clients_on_dh[4].has_been_configured)

        # order?
        self.assertEqual(clients_on_dh[0].order_of_the_day, orders_dict[0])
        self.assertEqual(clients_on_dh[1].order_of_the_day, orders_dict[7])
        self.assertEqual(clients_on_dh[2].order_of_the_day, orders_dict[9])
        self.assertEqual(clients_on_dh[3].order_of_the_day, orders_dict[4])
        self.assertEqual(clients_on_dh[4].order_of_the_day, orders_dict[6])


class TestMigrationApply0032(TestMigrations):
    """
    Refs #740.

    Naming rules in testing:
    - client000: 0 referent; 0 emergency; 0 referent AND emergency.
    - client010: 0 referent; 1 emergency; 0 referent AND emergency.
    - client100: 1 referent; 0 emergency; 0 referent AND emergency.
    - client001: 0 referent; 0 emergency; 1 referent AND emergency.
    - client234: 2 referent; 3 emergency; 4 referent AND emergency.

    I'm going to test client000 through client333.
    So 4*4*4=64 test cases in total.

    Additionally, because member.Referencing doesn't define unique_together,
    for client3xx test cases, I'm having 2 referents exactly the same.
    (member.EmergencyContact doesn't have this problem.)
    """
    migrate_from = '0031_client_option_allow_reverse_relation'
    migrate_to = '0032_relationship'

    # EmergencyContact.relationship has blank=True, null=True
    emgc_relationships = ['friend', None, 'son']
    referral_reasons = ['test1', '', '']
    referral_dates = [date(2001, 1, 1), date(2002, 2, 2), date(2003, 3, 3)]

    def setUpBeforeMigration(self, apps):
        Member = apps.get_model('member', 'Member')
        Client = apps.get_model('member', 'Client')
        Referencing = apps.get_model('member', 'Referencing')
        EmergencyContact = apps.get_model('member', 'EmergencyContact')

        for num_r in range(4):  # [0, 1, 2, 3]
            for num_e in range(4):
                for num_re in range(4):
                    # Create main client
                    name_main = "{}{}{}".format(num_r, num_e, num_re)
                    member_main = Member.objects.create(
                        firstname=name_main,  # Later we use this to query
                        lastname="main")
                    client_main = Client.objects.create(
                        billing_member=member_main,
                        member=member_main)

                    # Create referents
                    for i in range(num_r):
                        # Special case as described in docstring
                        if num_r == 3 and i == 2:  # last referent
                            member_ref = Member.objects.get(
                                firstname=name_main,
                                lastname='ref_#1')
                        else:
                            member_ref = Member.objects.create(
                                firstname=name_main,
                                lastname='ref_#{}'.format(i))
                        Referencing.objects.create(
                            referent=member_ref,
                            client=client_main,
                            referral_reason=self.referral_reasons[i],
                            date=self.referral_dates[i])
                        del member_ref  # avoid myself making errors below

                    # Create emergency contacts
                    for i in range(num_e):
                        member_emgc = Member.objects.create(
                            firstname=name_main,
                            lastname='emgc_#{}'.format(i))
                        EmergencyContact.objects.create(
                            member=member_emgc,
                            client=client_main,
                            relationship=self.emgc_relationships[i])
                        del member_emgc

                    # Create referent+emergency contacts
                    for i in range(num_re):
                        member_re = Member.objects.create(
                            firstname=name_main,
                            lastname='ref+emgc_#{}'.format(i))
                        Referencing.objects.create(
                            referent=member_re,
                            client=client_main,
                            referral_reason=self.referral_reasons[i],
                            date=self.referral_dates[i])
                        EmergencyContact.objects.create(
                            member=member_re,
                            client=client_main,
                            relationship=self.emgc_relationships[i])
                        del member_re

    def test_migrated_relationships(self):
        Member = self.apps.get_model('member', 'Member')
        Client = self.apps.get_model('member', 'Client')
        Relationship = self.apps.get_model('member', 'Relationship')

        from member.models import Relationship as _ref_Relationship  # noqa

        for num_r in range(4):  # [0, 1, 2, 3]
            for num_e in range(4):
                for num_re in range(4):
                    name_main = "{}{}{}".format(num_r, num_e, num_re)
                    fail_msg = (
                        "while testing: client{} "
                        "(see docstring)".format(name_main))
                    client_main = Client.objects.get(
                        member__firstname=name_main,
                        member__lastname="main")

                    # Check number of Relationship objects
                    self.assertEqual(
                        Relationship.objects.filter(
                            client=client_main,
                            # Attention: DB filter JSON field
                            type__contains=_ref_Relationship.REFERENT).count(),
                        # Special case when num_r == 3
                        (num_r if num_r != 3 else 2) + num_re,
                        msg=fail_msg)
                    self.assertEqual(
                        Relationship.objects.filter(
                            client=client_main,
                            # Attention: DB filter JSON field
                            type__contains=_ref_Relationship.EMERGENCY
                        ).count(),
                        num_e + num_re,
                        msg=fail_msg)
                    self.assertEqual(
                        Relationship.objects.filter(
                            client=client_main).count(),
                        # Special case when num_r == 3
                        (num_r if num_r != 3 else 2) + num_e + num_re,
                        msg=fail_msg)

                    # Check referents
                    for i in range(num_r):
                        sub_fail_msg = "{} -- Referent #{}".format(
                            fail_msg, i)
                        # Special case when num_r == 3
                        member_ref = Member.objects.get(
                            firstname=name_main,
                            lastname='ref_#{}'.format(
                                1 if (num_r == 3 and i == 2) else i))
                        r = Relationship.objects.get(
                            client=client_main,
                            member=member_ref)
                        self.assertEqual(r.nature, '??? (migration 0032)',
                                         msg=sub_fail_msg)
                        self.assertEqual(r.type,
                                         [_ref_Relationship.REFERENT],
                                         msg=sub_fail_msg)

                        # Special case when num_r == 3
                        # The ref_#1 will be overwritten by ref_#2, because
                        # in migrate 0032, Referencing objects are ordered by
                        # 'pk'.
                        correct_i = 2 if (num_r == 3 and i == 1) else i
                        self.assertEqual(r.extra_fields, {
                            'referral_date': str(
                                self.referral_dates[correct_i]),
                            'referral_reason': self.referral_reasons[correct_i]
                        }, msg=sub_fail_msg)
                        self.assertEqual(r.remark, '', msg=sub_fail_msg)
                        del member_ref  # avoid myself making errors below

                    # Check emergency contacts
                    for i in range(num_e):
                        sub_fail_msg = "{} -- Emergency #{}".format(
                            fail_msg, i)
                        member_emgc = Member.objects.get(
                            firstname=name_main,
                            lastname='emgc_#{}'.format(i))
                        r = Relationship.objects.get(
                            client=client_main,
                            member=member_emgc)
                        self.assertEqual(r.nature,
                                         self.emgc_relationships[i] or (
                                             "??? (migration 0032)"),
                                         msg=sub_fail_msg)
                        self.assertEqual(r.type,
                                         [_ref_Relationship.EMERGENCY],
                                         msg=sub_fail_msg)
                        self.assertEqual(r.extra_fields, {}, msg=sub_fail_msg)
                        self.assertEqual(r.remark, '', msg=sub_fail_msg)
                        del member_emgc

                    # Check referents+emergency contacts
                    for i in range(num_re):
                        sub_fail_msg = "{} -- Ref+Emgc #{}".format(
                            fail_msg, i)
                        member_re = Member.objects.get(
                            firstname=name_main,
                            lastname='ref+emgc_#{}'.format(i))
                        r = Relationship.objects.get(
                            client=client_main,
                            member=member_re)
                        self.assertEqual(r.nature,
                                         self.emgc_relationships[i] or (
                                             '??? (migration 0032)'),
                                         msg=sub_fail_msg)
                        self.assertEqual(sorted(r.type),
                                         sorted([_ref_Relationship.EMERGENCY,
                                                 _ref_Relationship.REFERENT]),
                                         msg=sub_fail_msg)
                        self.assertEqual(r.extra_fields, {
                            'referral_date': str(self.referral_dates[i]),
                            'referral_reason': self.referral_reasons[i]
                        }, msg=sub_fail_msg)
                        self.assertEqual(r.remark, '', msg=sub_fail_msg)
                        del member_re


class TestMigrationUnapply0032(TestMigrations):
    """
    Refs #740.

    Same naming rules as TestMigrationApply0032 (see docstring there).
    Also test from client000 through client333.
    But no special case for client3xx because of unique_together constraint.
    """

    migrate_from = '0032_relationship'
    migrate_to = '0031_client_option_allow_reverse_relation'

    natures = ['friend', 'son', 'government']
    remarks = ['remark1', 'remark2', 'remark3']
    extra_fields = [
        {'referral_reason': 'reason1', 'referral_date': date(2001, 1, 1)},
        # These invalid values may exist in database...
        {},
        ['a', 'b', 'c']
    ]

    def setUpBeforeMigration(self, apps):
        Member = apps.get_model('member', 'Member')
        Client = apps.get_model('member', 'Client')
        Relationship = apps.get_model('member', 'Relationship')

        from member.models import Relationship as _ref_Relationship  # noqa

        for num_r in range(4):  # [0, 1, 2, 3]
            for num_e in range(4):
                for num_re in range(4):
                    # Create main client
                    name_main = "{}{}{}".format(num_r, num_e, num_re)
                    member_main = Member.objects.create(
                        firstname=name_main,  # Later we use this to query
                        lastname="main")
                    client_main = Client.objects.create(
                        billing_member=member_main,
                        member=member_main)

                    # Create referents
                    for i in range(num_r):
                        member_ref = Member.objects.create(
                            firstname=name_main,
                            lastname='ref_#{}'.format(i))
                        Relationship.objects.create(
                            member=member_ref,
                            client=client_main,
                            nature=self.natures[i],
                            type=[_ref_Relationship.REFERENT],
                            extra_fields=self.extra_fields[i],
                            remark=self.remarks[i])
                        del member_ref  # avoid myself making errors below

                    # Create emergency contacts
                    for i in range(num_e):
                        member_emgc = Member.objects.create(
                            firstname=name_main,
                            lastname='emgc_#{}'.format(i))
                        Relationship.objects.create(
                            member=member_emgc,
                            client=client_main,
                            nature=self.natures[i],
                            type=[_ref_Relationship.EMERGENCY],
                            extra_fields=self.extra_fields[i],
                            remark=self.remarks[i])
                        del member_emgc  # avoid myself making errors below

                    # Create referent+emergency contacts
                    for i in range(num_re):
                        member_re = Member.objects.create(
                            firstname=name_main,
                            lastname='ref+emgc_#{}'.format(i))
                        Relationship.objects.create(
                            member=member_re,
                            client=client_main,
                            nature=self.natures[i],
                            type=[_ref_Relationship.EMERGENCY,
                                  _ref_Relationship.REFERENT],
                            extra_fields=self.extra_fields[i],
                            remark=self.remarks[i])
                        del member_re  # avoid myself making errors below

    def test_reversed_referencings_and_emergencycontacts(self):
        Member = self.apps.get_model('member', 'Member')
        Client = self.apps.get_model('member', 'Client')
        Referencing = self.apps.get_model('member', 'Referencing')
        EmergencyContact = self.apps.get_model('member', 'EmergencyContact')

        for num_r in range(4):  # [0, 1, 2, 3]
            for num_e in range(4):
                for num_re in range(4):
                    name_main = "{}{}{}".format(num_r, num_e, num_re)
                    fail_msg = (
                        "while testing: client{} "
                        "(see docstring)".format(name_main))
                    client_main = Client.objects.get(
                        member__firstname=name_main,
                        member__lastname="main")

                    # Check number of Referencing and EmergencyContact objects
                    self.assertEqual(
                        Referencing.objects.filter(
                            client=client_main).count(),
                        num_r + num_re,
                        msg=fail_msg)
                    self.assertEqual(
                        EmergencyContact.objects.filter(
                            client=client_main).count(),
                        num_e + num_re,
                        msg=fail_msg)

                    # Check referents
                    for i in range(num_r):
                        sub_fail_msg = "{} -- Referent #{}".format(
                            fail_msg, i)
                        member_ref = Member.objects.get(
                            firstname=name_main,
                            lastname='ref_#{}'.format(i))
                        r = Referencing.objects.get(
                            client=client_main,
                            referent=member_ref)
                        if isinstance(self.extra_fields[i], dict):
                            correct_referral_reason = self.extra_fields[i].get(
                                'referral_reason')
                            correct_date = self.extra_fields[i].get(
                                'referral_date')
                        else:
                            correct_referral_reason = None
                            correct_date = None

                        self.assertEqual(
                            r.referral_reason,
                            correct_referral_reason or (
                                '??? (reverse migration 0032)'),
                            msg=sub_fail_msg)
                        self.assertEqual(
                            r.date,
                            correct_date or date(1970, 1, 1),
                            msg=sub_fail_msg)
                        del member_ref  # avoid myself making errors below

                    # Check emergency contacts
                    for i in range(num_e):
                        sub_fail_msg = "{} -- Emergency #{}".format(
                            fail_msg, i)
                        member_emgc = Member.objects.get(
                            firstname=name_main,
                            lastname='emgc_#{}'.format(i))
                        ec = EmergencyContact.objects.get(
                            client=client_main,
                            member=member_emgc)
                        self.assertEqual(
                            ec.relationship,
                            self.natures[i],
                            msg=sub_fail_msg)
                        del member_emgc

                    # Check referents+emergency contacts
                    for i in range(num_re):
                        sub_fail_msg = "{} -- Ref+Emgc #{}".format(
                            fail_msg, i)
                        member_re = Member.objects.get(
                            firstname=name_main,
                            lastname='ref+emgc_#{}'.format(i))

                        r = Referencing.objects.get(
                            client=client_main,
                            referent=member_re)
                        if isinstance(self.extra_fields[i], dict):
                            correct_referral_reason = self.extra_fields[i].get(
                                'referral_reason')
                            correct_date = self.extra_fields[i].get(
                                'referral_date')
                        else:
                            correct_referral_reason = None
                            correct_date = None

                        self.assertEqual(
                            r.referral_reason,
                            correct_referral_reason or (
                                '??? (reverse migration 0032)'),
                            msg=sub_fail_msg)
                        self.assertEqual(
                            r.date,
                            correct_date or date(1970, 1, 1),
                            msg=sub_fail_msg)

                        ec = EmergencyContact.objects.get(
                            client=client_main,
                            member=member_re)
                        self.assertEqual(
                            ec.relationship,
                            self.natures[i],
                            msg=sub_fail_msg)

                        del member_re  # avoid myself making errors below
