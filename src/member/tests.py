import json

from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.management import call_command
from django.forms import BaseFormSet
from django.urls import reverse, reverse_lazy
from django.utils.six import StringIO
from django.test import TestCase, Client

from member.models import (
    Member, Client, Address, Referencing,
    Contact, Option, Client_option, Restriction, Route,
    Client_avoid_ingredient, Client_avoid_component,
    ClientScheduledStatus,
    CELL, HOME, EMAIL, DAYS_OF_WEEK
)
from meal.models import (
    Restricted_item, Ingredient, Component, COMPONENT_GROUP_CHOICES
)
from order.models import Order
from member.factories import(
    RouteFactory, ClientFactory, ClientScheduledStatusFactory,
    MemberFactory, EmergencyContactFactory
)
from meal.factories import IngredientFactory, ComponentFactory
from order.factories import OrderFactory
from member.forms import(
    ClientBasicInformation, ClientAddressInformation,
    ClientReferentInformation, ClientPaymentInformation,
    ClientRestrictionsInformation, ClientEmergencyContactInformation
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
        'work_information':
            client.client_referent.get().referent.work_information
            if client.client_referent.count()
            else '',
        'referral_reason':
            client.client_referent.get().referral_reason
            if client.client_referent.count()
            else '',
        'date':
            client.client_referent.get().date
            if client.client_referent.count()
            else '',
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


class ReferencingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        professional_member = Member.objects.create(firstname='Dr. John',
                                                    lastname='Taylor')
        billing_address = Address.objects.create(
            number=123, street='De Bullion',
            city='Montreal', postal_code='H3C4G5')
        beneficiary_member = Member.objects.create(firstname='Angela',
                                                   lastname='Desousa',
                                                   address=billing_address)
        client = Client.objects.create(
            member=beneficiary_member, billing_member=beneficiary_member)
        Referencing.objects.create(referent=professional_member, client=client,
                                   date=date(2015, 3, 15))

    def test_str_includes_all_names(self):
        """A reference listing shows by which member for which client"""
        professional_member = Member.objects.get(firstname='Dr. John')
        beneficiary_member = Member.objects.get(firstname='Angela')
        reference = Referencing.objects.get(referent=professional_member)
        self.assertTrue(professional_member.firstname in str(reference))
        self.assertTrue(professional_member.lastname in str(reference))
        self.assertTrue(beneficiary_member.firstname in str(reference))
        self.assertTrue(beneficiary_member.lastname in str(reference))


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

                # wednesday invalid
                "main_dish_wednesday_quantity": 0,
                "dessert_wednesday_quantity": 0,
                "size_wednesday": "R",

                # thursday invalid (no size)
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
            'dessert': 0,
            'diabetic': 2,
            'fruit_salad': 1,
            'green_salad': 0,
            'pudding': 0,
            'compote': 0
        })
        self.assertEqual(md['tuesday'], {
            'main_dish': 0,
            'size': 'L',
            'dessert': 0,
            'diabetic': 0,
            'fruit_salad': 0,
            'green_salad': 0,
            'pudding': 0,
            'compote': 1
        })
        self.assertEqual(md['wednesday'], None)
        self.assertEqual(md['thursday'], None)
        self.assertEqual(md['friday'], None)
        self.assertEqual(md['saturday'], None)
        self.assertEqual(md['sunday'], None)

    def test_client_meals_schedule(self):
        """
        Tests: Client.meals_schedule
        """
        ms = dict(self.clientTest.meals_schedule)
        self.assertEqual(ms['monday'], {
            'main_dish': 1,
            'size': 'R',
            'dessert': 0,
            'diabetic': 2,
            'fruit_salad': 1,
            'green_salad': 0,
            'pudding': 0,
            'compote': 0
        })
        self.assertEqual(ms['tuesday'], None)  # no delivery scheduled
        self.assertEqual(ms['wednesday'], None)
        self.assertEqual(ms['thursday'], None)
        self.assertEqual(ms['friday'], None)
        self.assertEqual(ms['saturday'], None)
        self.assertEqual(ms['sunday'], None)

    def test_client_meals_schedule_without_option(self):
        """
        Test when the client option 'meals_schedule' is not set.
        Refs #706.
        """
        self.clientOptionTest.delete()
        ms = dict(self.clientTest.meals_schedule)
        self.assertEqual(ms['monday'], None)
        self.assertEqual(ms['tuesday'], None)
        self.assertEqual(ms['wednesday'], None)
        self.assertEqual(ms['thursday'], None)
        self.assertEqual(ms['friday'], None)
        self.assertEqual(ms['saturday'], None)
        self.assertEqual(ms['sunday'], None)


class ClientEpisodicMealsPrefsTestCase(TestCase):

    fixtures = ['routes']

    @classmethod
    def setUpTestData(cls):
        cls.clientTest = ClientFactory()
        cls.posted_prefs = {
            'delivery_type': 'E',
            'size_default': 'L',
            'main_dish_default_quantity': 1,
            'dessert_default_quantity': 1,
            'diabetic_default_quantity': 0,
            'fruit_salad_default_quantity': 0,
            'green_salad_default_quantity': 1,
            'pudding_default_quantity': 0,
            'compote_default_quantity': 0,
        }

    def test_episodic_meals_prefs(self):
        """
        A Client_option's string representation includes the name
        of the client and the name of the option.
        """
        self.clientTest.set_meals_prefs(self.posted_prefs)
        clientPrefs = self.clientTest.get_meals_prefs()
        self.assertEqual(clientPrefs["maindish_s"], 'L')
        self.assertEqual(clientPrefs["maindish_q"], 1)
        self.assertEqual(clientPrefs["dst_q"], 1)
        self.assertEqual(clientPrefs["diabdst_q"], 0)
        self.assertEqual(clientPrefs["fruitsld_q"], 0)
        self.assertEqual(clientPrefs["greensld_q"], 1)
        self.assertEqual(clientPrefs["pudding_q"], 0)
        self.assertEqual(clientPrefs["compot_q"], 0)


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
                kwargs={'step': 'basic_information'}
            ),
            follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_adress_information(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': 'address_information'}
            ),
            follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_acces_to_form_by_url_referent_information(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': 'referent_information'}
            ),
            follow=True
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

    def test_acces_to_form_by_url_emergency_contact(self):
        result = self.client.get(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': 'emergency_contact'}
            ),
            follow=True
        )
        self.assertEqual(result.status_code, 200)

    def test_form_save_data_all_different_members(self):
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

        referent_information_data = {
            "client_wizard-current_step": "referent_information",
            "referent_information-firstname": "Referent",
            "referent_information-lastname": "Testing",
            "referent_information-email": "referent@testing.com",
            "referent_information-work_phone": "458-458-4584 #458",
            "referent_information-work_information": "CLSC",
            "referent_information-date": "2012-12-12",
            "referent_information-referral_reason": "Testing referral reason",
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

        emergency_contact_data = {
            "client_wizard-current_step": "emergency_contacts",
            "emergency_contacts-TOTAL_FORMS": "1",
            "emergency_contacts-INITIAL_FORMS": "1",
            "emergency_contacts-MIN_NUM_FORMS": "0",
            "emergency_contacts-MAX_NUM_FORMS": "1000",
            "emergency_contacts-0-firstname": "Emergency",
            "emergency_contacts-0-lastname": "User",
            "emergency_contacts-0-work_phone": "555-444-5555",
            "emergency_contacts-0-relationship": "friend",
        }

        stepsdata = [
            ('basic_information', basic_information_data),
            ('address_information', address_information_data),
            ('referent_information', referent_information_data),
            ('payment_information', payment_information_data),
            ('dietary_restriction', restriction_information_data),
            ('emergency_contacts', emergency_contact_data)
        ]

        for step, data in stepsdata:
            response = self.client.post(
                reverse_lazy('member:member_step', kwargs={'step': step}),
                data,
                follow=True
            )

        member = Member.objects.get(firstname="User")
        self._test_assert_member_info_all_different_members(member)

        client = Client.objects.get(member=member)
        self._test_assert_client_info_all_different_members(client)

        # Test the client view
        self._test_client_detail_view_all_different_members(client)
        self._test_client_view_preferences(client)

    def _test_assert_member_info_all_different_members(self, member):
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

    def _test_assert_client_info_all_different_members(self, client):
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

        # test_referent_name:
        self.assertEqual(
            client.client_referent.first().referent.firstname,
            "Referent"
        )
        self.assertEqual(
            client.client_referent.first().referent.lastname,
            "Testing"
        )

        # test referent contact infos (email and work phone)
        self.assertEqual(
            client.client_referent.first().referent.email,
            "referent@testing.com"
        )
        self.assertEqual(
            client.client_referent.first().referent.work_phone,
            "458-458-4584 #458"
        )

        # test_referent_work_information:
        self.assertEqual(
            client.client_referent.first().referent.work_information,
            "CLSC"
        )

        # test_referral_date(self):
        self.assertEqual(
            client.client_referent.first().date,
            date(2012, 12, 12)
        )

        # test_referral_reason:
        self.assertEqual(
            client.client_referent.first().referral_reason,
            "Testing referral reason"
        )

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

        emergency_contacts = client.emergency_contacts.all()
        #  test_emergency_contact_name:
        self.assertIn(
            "Emergency",
            [c.firstname for c in emergency_contacts]
        )
        self.assertIn(
            "User",
            [c.lastname for c in emergency_contacts]
        )

        #  test_emergency_contact_type:
        self.assertIn(
            "Work phone",
            [c.member_contact.first().type for c in emergency_contacts],
        )

        #  test_emergency_contact_value:
        self.assertIn(
            "555-444-5555",
            [c.member_contact.first().value for c in emergency_contacts],
        )

        # test emergency_contact.relationship:
        self.assertIn(
            "friend",
            [ec.relationship for ec in client.emergencycontact_set.all()],
        )

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

    def _test_client_detail_view_all_different_members(self, client):
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

    def test_form_save_data_same_members(self):
        basic_information_data = {
            "client_wizard-current_step": "basic_information",
            "basic_information-firstname": "Same",
            "basic_information-lastname": "User",
            "basic_information-language": "fr",
            "basic_information-gender": "M",
            "basic_information-birthdate": "1986-06-06",
            "basic_information-home_phone": "514-868-8686",
            "basic_information-cell_phone": "438-000-0000",
            "basic_information-email": "test@example.com",
            "basic_information-alert": "Testing alert message",
            "wizard_goto_step": ""
        }

        address_information_data = {
            "client_wizard-current_step": "address_information",
            "address_information-street": "8686 rue clark",
            "address_information-apartment": "86",
            "address_information-city": "Montreal",
            "address_information-postal_code": "H8C6C8",
            "address_information-route": self.route.id,
            "address_information-latitude": 45.5343077,
            "address_information-longitude": -73.620735,
            "address_information-distance": 4.062611162244175,
            "wizard_goto_step": "",
        }

        referent_information_data = {
            "client_wizard-current_step": "referent_information",
            "referent_information-firstname": "Same",
            "referent_information-lastname": "User",
            "referent_information-work_information": "CLSC",
            "referent_information-date": "2012-06-06",
            "referent_information-referral_reason": "Testing referral reason",
            "wizard_goto_step": "",
        }

        payment_information_data = {
            "client_wizard-current_step": "payment_information",
            "payment_information-same_as_client": True,
            "payment_information-billing_payment_type": "3rd",
            "payment_information-facturation": "default",
            "address_information-latitude": 0.0,
            "address_information-longitude": 0.0,
            "address_information-distance": 0.0,
            "wizard_goto_step": "",
        }

        restriction_information_data = {
            "client_wizard-current_step": "dietary_restriction",
            "dietary_restriction-status": "on",
            "dietary_restriction-delivery_type": "O",
            "dietary_restriction-meals_schedule": "monday",
            "dietary_restriction-meal_default": "1",
            "wizard_goto_step": ""
        }

        emergency_contact_data = {
            "client_wizard-current_step": "emergency_contacts",
            "emergency_contacts-TOTAL_FORMS": "1",
            "emergency_contacts-INITIAL_FORMS": "1",
            "emergency_contacts-MIN_NUM_FORMS": "0",
            "emergency_contacts-MAX_NUM_FORMS": "1000",
            "emergency_contacts-0-firstname": "Same",
            "emergency_contacts-0-lastname": "User",
            "emergency_contacts-0-cell_phone": "514-868-8686",
            "emergency_contacts-0-relationship": "friend"
        }

        stepsdata = [
            ('basic_information', basic_information_data),
            ('address_information', address_information_data),
            ('referent_information', referent_information_data),
            ('payment_information', payment_information_data),
            ('dietary_restriction', restriction_information_data),
            ('emergency_contacts', emergency_contact_data)
        ]

        for step, data in stepsdata:
            self.client.post(
                reverse_lazy('member:member_step', kwargs={'step': step}),
                data,
                follow=True
            )

        member = Member.objects.get(firstname="Same")
        self._test_assert_member_info_same_members(member)

        client = Client.objects.get(member=member)
        self._test_assert_client_info_same_members(client)

        self._test_client_detail_view_same_members(client)
        self._test_client_list_view_same_members()

    def _test_assert_member_info_same_members(self, member):
        # test firstname and lastname
        self.assertEqual(member.firstname, "Same")
        self.assertEqual(member.lastname, "User")

        # test_home_phone_member:
        self.assertEqual(member.home_phone, '514-868-8686')
        self.assertTrue(member.home_phone.startswith('514'))
        self.assertEqual(member.email, 'test@example.com')
        self.assertEqual(member.cell_phone, '438-000-0000')

        # test_client_contact_type:
        self.assertEqual(member.member_contact.first().type, "Home phone")

        # test_client_address:
        self.assertEqual(member.address.street, "8686 rue clark")
        self.assertEqual(member.address.postal_code, "H8C 6C8")
        self.assertEqual(member.address.apartment, "86")
        self.assertEqual(member.address.city, "Montreal")

    def _test_assert_client_info_same_members(self, client):
        # test_client_alert:
        self.assertEqual(client.alert, "Testing alert message")

        # test_client_languages:
        self.assertEqual(client.language, "fr")

        # test_client_birthdate:
        self.assertEqual(client.birthdate, date(1986, 6, 6))

        # test_client_gender:
        self.assertEqual(client.gender, "M")

        # test client delivery type
        self.assertEqual(client.delivery_type, 'O')

        # test referent member is emergency member
        self.assertIn(
            client.client_referent.first().referent.id,
            [c.pk for c in client.emergency_contacts.all()]
        )

        # test_referent_name:
        self.assertEqual(
            client.client_referent.first().referent.firstname,
            "Same"
        )
        self.assertEqual(
            client.client_referent.first().referent.lastname,
            "User"
        )

        # test_referent_work_information:
        self.assertEqual(
            client.client_referent.first().referent.work_information,
            "CLSC"
        )

        # test_referral_date(self):
        self.assertEqual(
            client.client_referent.first().date,
            date(2012, 6, 6)
        )

        # test_referral_reason:
        self.assertEqual(
            client.client_referent.first().referral_reason,
            "Testing referral reason"
        )

        # test client member is billing member
        self.assertEqual(client.member.id, client.billing_member.id)

        # test_billing_name:
        self.assertEqual(client.billing_member.firstname, "Same")
        self.assertEqual(client.billing_member.lastname, "User")

        #  test_billing_type:
        self.assertEqual(client.billing_payment_type, "3rd")

        #  test_billing_address:
        self.assertEqual(client.billing_member.address.city, "Montreal")

        self.assertEqual(
            client.billing_member.address.street,
            "8686 rue clark"
        )
        self.assertEqual(client.billing_member.address.postal_code, "H8C 6C8")

        #  test_billing_rate_type:
        self.assertEqual(client.rate_type, 'default')

        emergency_contacts = client.emergency_contacts.all()
        #  test_emergency_contact_name:
        self.assertIn("Same", [c.firstname for c in emergency_contacts])
        self.assertIn("User", [c.lastname for c in emergency_contacts])

        #  test_emergency_contact_type:
        self.assertIn(
            "Home phone",
            [c.member_contact.first().type for c in emergency_contacts],
        )

        #  test_emergency_contact_value:
        self.assertIn(
            "514-868-8686",
            [c.member_contact.first().value for c in emergency_contacts],
        )

        # test emergency_contact.relationship:
        self.assertIn(
            "friend",
            [ec.relationship for ec in client.emergencycontact_set.all()],
        )

    def _test_client_detail_view_same_members(self, client):
        response = self.client.get(
            reverse_lazy('member:client_information', kwargs={'pk': client.id})
        )
        self.assertTrue(b"User" in response.content)
        self.assertTrue(b"Same" in response.content)
        self.assertTrue(b"Home phone" in response.content)
        self.assertTrue(b"8686 rue clark" in response.content)
        self.assertTrue(b"H8C 6C8" in response.content)
        self.assertTrue(b"Montreal" in response.content)
        self.assertTrue(b"Testing alert message" in response.content)
        self.assertTrue(b"514-868-8686" in response.content)

    def _test_client_list_view_same_members(self):
        response = self.client.get(reverse_lazy('member:list'))
        self.assertTrue(b"User" in response.content)
        self.assertTrue(b"Same" in response.content)
        self.assertTrue(b"30 years old" in response.content)
        self.assertTrue(b"Active" in response.content)
        self.assertTrue(b"Ongoing" in response.content)
        self.assertTrue(b"514-868-8686" in response.content)

    def test_form_validate_data(self):
        """Test all the step of the form with and without wrong data"""
        self._test_basic_information_with_errors()
        self._test_basic_information_without_errors()
        self._test_address_information_with_errors()
        self._test_address_information_without_errors()
        self._test_referent_information_with_errors()
        self._test_referent_information_without_errors()
        self._test_payment_information_with_errors()
        self._test_payment_information_without_errors()
        self._test_step_dietary_restriction_with_errors()
        self._test_step_dietary_restriction_without_errors()
        self._test_step_emergency_contact_with_errors()
        self._test_step_emergency_contact_without_errors()

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
                             'This field is required.')
        self.assertFormError(error_response, 'form',
                             'birthdate',
                             'This field is required.')
        self.assertFormError(error_response, 'form',
                             'email',
                             'At least one contact information is required.')
        self.assertFormError(error_response, 'form',
                             'home_phone',
                             'At least one contact information is required.')
        self.assertFormError(error_response, 'form',
                             'cell_phone',
                             'At least one contact information is required.')

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
                kwargs={'step': "basic_information"}
            ),
            basic_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': "address_information"}
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
                kwargs={'step': "address_information"}
            ),
            address_information_data_with_error,
            follow=True
        )

        # The response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'street',
                             'This field is required.')
        self.assertFormError(response_error, 'form',
                             'city',
                             'This field is required.')
        self.assertFormError(response_error, 'form',
                             'postal_code',
                             'This field is required.')

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
                kwargs={'step': "address_information"}),
            address_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': "referent_information"}
        ))

        # The response is the next step of the form with no errors messages.
        form = response.context['form']
        self.assertFalse(form.errors)
        self.assertNotIn('street', form.fields)
        self.assertNotIn('apartment', form.fields)
        # New form field in the next step
        self.assertIn('work_information', form.fields)

    def _test_referent_information_with_errors(self):
        # Data for the address_information step with errors.
        referent_information_data_with_error = {
            "client_wizard-current_step": "referent_information",
            "referent_information-member": "",
            "referent_information-firstname": "",
            "referent_information-lastname": "",
            "referent_information-work_information": "",
            "referent_information-date": "",
            "referent_information-referral_reason": "",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "referent_information"}
            ),
            referent_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'member',
                             'This field is required '
                             'unless you add a new member.')
        self.assertFormError(response_error, 'form',
                             'firstname',
                             'This field is required unless '
                             'you chose an existing member.')
        self.assertFormError(response_error, 'form',
                             'lastname',
                             'This field is required unless '
                             'you chose an existing member.')
        self.assertFormError(response_error, 'form',
                             'work_information',
                             'This field is required unless '
                             'you chose an existing member.')
        self.assertFormError(response_error, 'form',
                             'date',
                             'This field is required.')
        self.assertFormError(response_error, 'form',
                             'referral_reason',
                             'This field is required.')

        referent_information_data_with_error = {
            "client_wizard-current_step": "referent_information",
            "referent_information-member": "[0] NotValid Member",
            "referent_information-firstname": "",
            "referent_information-lastname": "",
            "referent_information-work_information": "CLSC",
            "referent_information-date": "2012-12-12",
            "referent_information-referral_reason": "Testing referral reason",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "referent_information"}
            ),
            referent_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'member',
                             'Not a valid member, '
                             'please chose an existing member.')

    def _test_referent_information_without_errors(self):
        pk = Member.objects.get(firstname="First").id
        referent_information_data = {
            "client_wizard-current_step": "referent_information",
            "referent_information-member": "[{}] First Member".format(pk),
            "referent_information-firstname": "",
            "referent_information-lastname": "",
            "referent_information-work_information": "CLSC",
            "referent_information-date": "2012-12-12",
            "referent_information-referral_reason": "Testing referral reason",
            "wizard_goto_step": "",
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "referent_information"}
            ),
            referent_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': "payment_information"}
        ))

        # The response is the next step of the form with no errors messages.
        form = response.context['form']
        self.assertFalse(form.errors)
        self.assertNotIn('work_information', form.fields)
        # New form field in the next step
        self.assertIn('billing_payment_type', form.fields)

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
                kwargs={'step': "payment_information"}
            ),
            payment_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'billing_payment_type',
                             'Select a valid choice. INVALID is not '
                             'one of the available choices.')
        self.assertFormError(response_error, 'form',
                             'member',
                             'This member has not a valid address, '
                             'please add a valid address to this member, '
                             'so it can be used for the billing.')

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
                kwargs={'step': "payment_information"}
            ),
            payment_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'street',
                             'This field is required')
        self.assertFormError(response_error, 'form',
                             'city',
                             'This field is required')
        self.assertFormError(response_error, 'form',
                             'postal_code',
                             'This field is required')

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
                kwargs={'step': "payment_information"}
            ),
            payment_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': "dietary_restriction"}
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
                kwargs={'step': "dietary_restriction"}
            ),
            restriction_information_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormError(response_error, 'form',
                             'delivery_type',
                             'This field is required.')
        self.assertFormError(response_error, 'form',
                             'meals_schedule',
                             'Select a valid choice.  is not '
                             'one of the available choices.')

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

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "dietary_restriction"}
            ),
            restriction_information_data,
            follow=True
        )

        # Check redirect (successful POST)
        self.assertRedirects(response, reverse_lazy(
            'member:member_step',
            kwargs={'step': "emergency_contacts"}
        ))

        # The response is the next step of the form with no errors messages.
        formset = response.context['form']
        self.assertIsInstance(formset, BaseFormSet)
        self.assertFalse(formset.errors)
        for form in formset.forms:
            self.assertNotIn('status', form.fields)
            self.assertNotIn('delivery_type', form.fields)
            self.assertNotIn('meals_schedule', form.fields)
            # New form field in the next step
            self.assertIn('relationship', form.fields)

    def _test_step_emergency_contact_with_errors(self):
        # Data for the address_information step with errors.
        emergency_contact_data_with_error = {
            "client_wizard-current_step": "emergency_contacts",
            "emergency_contacts-TOTAL_FORMS": "1",
            "emergency_contacts-INITIAL_FORMS": "1",
            "emergency_contacts-MIN_NUM_FORMS": "0",
            "emergency_contacts-MAX_NUM_FORMS": "1000",
            "emergency_contacts-0-firstname": "",
            "emergency_contacts-0-lastname": "",
            "emergency_contacts-0-home_phone": "",
            "emergency_contacts-0-work_phone": "",
            "emergency_contacts-0-cell_phone": "",
            "emergency_contacts-0-email": "",
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "emergency_contacts"}
            ),
            emergency_contact_data_with_error,
            follow=True
        )

        # Validate that the response is the same form with the errors messages.
        self.assertTrue(response_error.context['form'].errors)
        self.assertFormsetError(response_error, 'form', 0,
                                'cell_phone',
                                'At least one emergency contact is required.')
        self.assertFormsetError(response_error, 'form', 0,
                                'work_phone',
                                'At least one emergency contact is required.')
        self.assertFormsetError(response_error, 'form', 0,
                                'email',
                                'At least one emergency contact is required.')
        self.assertFormsetError(response_error, 'form', 0,
                                'lastname',
                                'This field is required unless '
                                'you chose an existing member.')
        self.assertFormsetError(response_error, 'form', 0,
                                'firstname',
                                'This field is required unless '
                                'you chose an existing member.')

    def _test_step_emergency_contact_without_errors(self):
        # Data for the address_information step without errors.
        pk = Member.objects.get(firstname="First").id
        emergency_contact_data = {
            "client_wizard-current_step": "emergency_contacts",
            "emergency_contacts-TOTAL_FORMS": "1",
            "emergency_contacts-INITIAL_FORMS": "1",
            "emergency_contacts-MIN_NUM_FORMS": "0",
            "emergency_contacts-MAX_NUM_FORMS": "1000",
            "emergency_contacts-0-member": "[{}] First Member".format(pk),
            "emergency_contact-0-firstname": "Emergency",
            "emergency_contact-0-lastname": "User",
            "emergency_contact-0-work_phone": "514-222-3333",
            "emergency_contact-0-relationship": "friend"
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "emergency_contacts"}
            ),
            emergency_contact_data,
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


class ClientStatusUpdateAndScheduleCase(TestCase):

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
        self.assertTrue(b'This field is required' in response.content)

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

    def test_view_client_status_delete_pair_base(self):
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
                'end_date': '2018-10-02',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )

        self.assertEqual(2, ClientScheduledStatus.objects.count())

        client_status_base = ClientScheduledStatus.objects.get(
            change_date='2018-09-23'
        )
        self.client.post(
            reverse_lazy(
                'member:delete_status',
                kwargs={'pk': client_status_base.id}
            )
        )

        self.assertEqual(0, ClientScheduledStatus.objects.count())

    def test_view_client_status_delete_pair_automatically_created(self):
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
                'end_date': '2018-10-02',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            follow=True
        )

        self.assertEqual(2, ClientScheduledStatus.objects.count())

        client_status_base = ClientScheduledStatus.objects.get(
            change_date='2018-10-02'
        )
        self.client.post(
            reverse_lazy(
                'member:delete_status',
                kwargs={'pk': client_status_base.id}
            )
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
        self.assertEqual(str(client.member.address.latitude),
                         data.get('latitude'))
        self.assertEqual(str(client.member.address.longitude),
                         data.get('longitude'))


class ClientUpdateReferentInformationTestCase(ClientUpdateTestCase):

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
            'member': '[0] Not Valid',
            'information': 'CLSC',
            'date': '2012-12-12',
            'referral_reason': 'Testing referral reason',
        })
        form = ClientReferentInformation(data=data)
        self.assertFalse(form.is_valid())
        data.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': None,
            'postal_code': None,
            'member': '[{}] {} {}'.format(
                client.client_referent.first().referent.id,
                client.client_referent.first().referent.firstname,
                client.client_referent.first().referent.lastname
            ),
            'information': 'CLSC',
            'date': '2012-12-12',
            'referral_reason': 'Testing referral reason'
        })
        form = ClientReferentInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_update_referent_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        referent = MemberFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data.update({
            'firstname': None,
            'lastname': None,
            'street': None,
            'city': None,
            'apartment': None,
            'postal_code': None,
            'member': '[{}] {} {}'.format(
                referent.id,
                referent.firstname,
                referent.lastname
            ),
            'information': 'CLSC',
            'date': '2012-12-12',
            'referral_reason': 'Testing referral reason',
        })

        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_referent_information',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertEqual(
            client.client_referent.first().referent.id,
            referent.id
        )
        self.assertEqual(
            client.client_referent.first().referent.firstname,
            referent.firstname
        )
        self.assertEqual(
            client.client_referent.first().referent.lastname,
            referent.lastname
        )


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
        day_count = 0
        for day, v in DAYS_OF_WEEK:
            for component, v in COMPONENT_GROUP_CHOICES:
                meals_default = Client.get_meal_defaults(
                    client, component, day_count)
                data[component + '_' + day + '_quantity'] = meals_default[0]
                if component == 'main_dish':
                    data['size_' + day] = meals_default[1]
            day_count += 1

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


class ClientUpdateEmergencyInformationTestCase(ClientUpdateTestCase):

    def test_form_validation_existing_member(self):
        """
        Test validation form.
        """
        emergency_contact = EmergencyContactFactory()
        client = emergency_contact.client
        data = load_initial_data(client)
        data.update({
            'firstname': None,
            'lastname': None,
            'member': '[0] Not Valid',
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertFalse(form.is_valid())
        member = emergency_contact.member
        data.update({
            'firstname': None,
            'lastname': None,
            'member': '[{}] {} {}'.format(
                member.id,
                member.firstname,
                member.lastname
            ),
            'relationship': None,
        })

        form = ClientEmergencyContactInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_form_validation_new_emergency_member(self):
        """
        Test validation form.
        """
        client = ClientFactory()
        data = load_initial_data(client)
        data.update({
            'firstname': None,
            'lastname': None,
            'member': None,
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'firstname': 'test',
            'lastname': 'test',
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'cell_phone': '514-122-3333'
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertTrue(form.is_valid())

        data['cell_phone'] = None
        data.update({
            'work_phone': '514-122-3333'
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertTrue(form.is_valid())

        data['work_phone'] = None
        data.update({
            'email': 'invalid email'
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertFalse(form.is_valid())

        data.update({
            'email': 'valid@email.com'
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_update_emergency_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        emergency = MemberFactory()  # new emergency
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data.update({
            "emergency_contacts-TOTAL_FORMS": "1",
            "emergency_contacts-INITIAL_FORMS": "1",
            "emergency_contacts-MIN_NUM_FORMS": "0",
            "emergency_contacts-MAX_NUM_FORMS": "1000",
            "emergency_contacts-0-firstname": None,
            "emergency_contacts-0-lastname": None,
            'emergency_contacts-0-member': '[{}] {} {}'.format(
                emergency.id,
                emergency.firstname,
                emergency.lastname
            )
        })

        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_emergency_contacts',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertIn(
            emergency.id,
            [c.pk for c in client.emergency_contacts.all()]
        )
        self.assertIn(
            emergency.firstname,
            [c.firstname for c in client.emergency_contacts.all()]
        )
        self.assertIn(
            emergency.lastname,
            [c.lastname for c in client.emergency_contacts.all()]
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
            'step': 'referent_information'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'payment_information'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'dietary_restriction'
        }))
        check(reverse('member:member_step', kwargs={
            'step': 'emergency_contact'
        }))
        check(reverse('member:list'))
        check(reverse('member:search'))
        check(reverse('member:view', kwargs={'pk': 1}))
        check(reverse('member:list_orders', kwargs={'pk': 1}))
        check(reverse('member:client_information', kwargs={'pk': 1}))
        check(reverse('member:client_referent', kwargs={'pk': 1}))
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
        check(reverse('member:client_meals_pref', kwargs={'pk': 1}))
        check(reverse('member:member_update_basic_information', kwargs={
            'pk': 1
        }))
        check(reverse('member:member_update_address_information', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_referent_information', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_payment_information', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_dietary_restriction', kwargs={
            'pk': 1
        }))

        check(reverse('member:member_update_emergency_contacts', kwargs={
            'pk': 1
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


class ClientReferentViewTestCase(SousChefTestMixin, TestCase):
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


class ClientUpdateReferentInformationViewTestCase(SousChefTestMixin, TestCase):
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
            'member:member_update_referent_information',
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
            'member:member_update_referent_information',
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


class ClientUpdateEmergencyContactInformationViewTestCase(
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
            'member:member_update_emergency_contacts',
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
            'member:member_update_emergency_contacts',
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
