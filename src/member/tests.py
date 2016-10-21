import datetime
import json
from django.test import TestCase, Client
from member.models import Member, Client, User, Address, Referencing
from member.models import Contact, Option, Client_option, Restriction, Route
from member.models import Client_avoid_ingredient, Client_avoid_component
from member.models import ClientScheduledStatus
from member.models import CELL, HOME, EMAIL, DAYS_OF_WEEK
from meal.models import (
    Restricted_item, Ingredient, Component, COMPONENT_GROUP_CHOICES
)
from datetime import date
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from order.models import Order
from member.factories import(
    RouteFactory, ClientFactory, ClientScheduledStatusFactory, MemberFactory
)
from meal.factories import IngredientFactory, ComponentFactory
from django.core.management import call_command
from django.utils.six import StringIO
from order.factories import OrderFactory
from member.forms import(
    ClientBasicInformation, ClientAddressInformation,
    ClientReferentInformation, ClientPaymentInformation,
    ClientRestrictionsInformation, ClientEmergencyContactInformation
)


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
            client.client_referent.get().work_information
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
        self.assertEquals(self.member.cell_phone, '438-000-0000')
        self.assertTrue(
            self.member.add_contact_information(EMAIL, 'admin@example.com')
        )
        self.assertEquals(self.member.email, 'admin@example.com')

    def test_add_contact_information_empty(self):
        """
        Passing an empty value should not update nor create anything, unless
        the force_update parameter was passed.
        """
        self.member.add_contact_information(CELL, '438-000-0000')
        self.assertEquals(self.member.cell_phone, '438-000-0000')
        self.assertFalse(
            self.member.add_contact_information(CELL, '')
        )
        self.assertEquals(self.member.cell_phone, '438-000-0000')
        self.assertFalse(
            self.member.add_contact_information(CELL, '', True)
        )
        self.assertEquals(self.member.cell_phone, '')

    def test_update_contact_information(self):
        """
        Test the add_contact_information method when a contact information
        of the given type already exists. The contact information should be
        updated, instead of creating a new one.
        """
        self.assertFalse(
            self.member.add_contact_information(HOME, '514-000-0000')
        )
        self.assertEquals(self.member.home_phone, '514-000-0000')


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
        cls.ss_client = ClientFactory(
            birthdate=date(1980, 4, 19),
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
        self.assertEqual(self.ss_client.age, 36)

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
            "address_information-postal_code": "H3C2C2",
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
            "payment_information-billing_payment_type": "check",
            "payment_information-facturation": "default",
            "payment_information-street": "111 rue clark",
            "payment_information-apartement": "222",
            "payment_information-city": "Montreal",
            "payment_information-postal_code": "H2C3G4",
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
            "client_wizard-current_step": "emergency_contact",
            "emergency_contact-firstname": "Emergency",
            "emergency_contact-lastname": "User",
            "emergency_contact-contact_type": "Home phone",
            "emergency_contact-contact_value": "555-444-5555"
        }

        stepsdata = [
            ('basic_information', basic_information_data),
            ('address_information', address_information_data),
            ('referent_information', referent_information_data),
            ('payment_information', payment_information_data),
            ('dietary_restriction', restriction_information_data),
            ('emergency_contact', emergency_contact_data)
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
        self.assertEquals(member.email, 'test@example.com')
        self.assertEquals(member.cell_phone, '438-000-0000')

        # test_client_contact_type:
        self.assertEqual(member.member_contact.first().type, "Home phone")

        # test_client_address:
        self.assertEqual(member.address.street, "555 rue clark")
        self.assertEqual(member.address.postal_code, "H3C2C2")
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
            client.client_referent.first().work_information,
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
        self.assertEqual(client.billing_payment_type, "check")

        #  test_billing_address:
        self.assertEqual(client.billing_member.address.city, "Montreal")
        self.assertEqual(client.billing_member.address.street, "111 rue clark")
        self.assertEqual(client.billing_member.address.postal_code, "H2C3G4")

        #  test_billing_rate_type:
        self.assertEqual(client.rate_type, 'default')

        #  test_emergency_contact_name:
        self.assertEqual(client.emergency_contact.firstname, "Emergency")
        self.assertEqual(client.emergency_contact.lastname, "User")

        #  test_emergency_contact_type:
        self.assertEqual(
            client.emergency_contact.member_contact.first().type,
            "Home phone"
        )

        #  test_emergency_contact_value:
        self.assertEqual(
            client.emergency_contact.member_contact.first().value,
            "555-444-5555"
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
        self.assertTrue(b"H3C2C2" in response.content)
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
            "payment_information-billing_payment_type": "check",
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
            "client_wizard-current_step": "emergency_contact",
            "emergency_contact-firstname": "Same",
            "emergency_contact-lastname": "User",
            "emergency_contact-contact_type": "Home phone",
            "emergency_contact-contact_value": "514-868-8686"
        }

        stepsdata = [
            ('basic_information', basic_information_data),
            ('address_information', address_information_data),
            ('referent_information', referent_information_data),
            ('payment_information', payment_information_data),
            ('dietary_restriction', restriction_information_data),
            ('emergency_contact', emergency_contact_data)
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
        self.assertTrue(member.home_phone.startswith('514'))
        self.assertEquals(member.email, 'test@example.com')
        self.assertEquals(member.cell_phone, '438-000-0000')

        # test_client_contact_type:
        self.assertEqual(member.member_contact.first().type, "Home phone")

        # test_client_address:
        self.assertEqual(member.address.street, "8686 rue clark")
        self.assertEqual(member.address.postal_code, "H8C6C8")
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
        self.assertEqual(
            client.client_referent.first().referent.id,
            client.emergency_contact.id
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
            client.client_referent.first().work_information,
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
        self.assertEqual(client.billing_payment_type, "check")

        #  test_billing_address:
        self.assertEqual(client.billing_member.address.city, "Montreal")
        self.assertEqual(
            client.billing_member.address.street,
            "8686 rue clark"
        )
        self.assertEqual(client.billing_member.address.postal_code, "H8C6C8")

        #  test_billing_rate_type:
        self.assertEqual(client.rate_type, 'default')

        #  test_emergency_contact_name:
        self.assertEqual(client.emergency_contact.firstname, "Same")
        self.assertEqual(client.emergency_contact.lastname, "User")

        #  test_emergency_contact_type:
        self.assertEqual(
            client.emergency_contact.member_contact.first().type,
            "Home phone"
        )

        #  test_emergency_contact_value:
        self.assertEqual(
            client.emergency_contact.member_contact.first().value,
            "514-868-8686"
        )

    def _test_client_detail_view_same_members(self, client):
        response = self.client.get(
            reverse_lazy('member:client_information', kwargs={'pk': client.id})
        )
        self.assertTrue(b"User" in response.content)
        self.assertTrue(b"Same" in response.content)
        self.assertTrue(b"Home phone" in response.content)
        self.assertTrue(b"8686 rue clark" in response.content)
        self.assertTrue(b"H8C6C8" in response.content)
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
        self.assertTrue(b'Required information' in error_response.content)
        self.assertTrue(b'lastname' in error_response.content)
        self.assertTrue(b'birthdate' in error_response.content)
        self.assertTrue(b'This field is required' in error_response.content)

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

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(b'gender' not in response.content)
        self.assertTrue(b'contact_value' not in response.content)
        self.assertTrue(b'This field is required' not in response.content)
        # HTML from the next step
        self.assertTrue(b'street' in response.content)

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
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'street' in response_error.content)
        self.assertTrue(b'apartment' in response_error.content)
        self.assertTrue(b'city' in response_error.content)
        self.assertTrue(b'This field is required' in response_error.content)

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

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' not in response.content)
        # self.assertTrue(b'street' not in response.content)
        # self.assertTrue(b'apartment' not in response.content)
        self.assertTrue(b'This field is required' not in response.content)
        # HTML from the next step
        self.assertTrue(b'work_information' in response.content)

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
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'member' in response_error.content)
        self.assertTrue(b'work_information' in response_error.content)
        self.assertTrue(b'This field is required' in response_error.content)

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
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'member' in response_error.content)
        self.assertTrue(b'work_information' in response_error.content)
        self.assertTrue(b'Not a valid member' in response_error.content)

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

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(b'work_information' not in response.content)
        self.assertTrue(b'This field is required' not in response.content)
        # HTML from the next step
        self.assertTrue(b'billing_payment_type' in response.content)

    def _test_payment_information_with_errors(self):
        # Data for the address_information step with errors.
        pk = Member.objects.get(firstname="Second").id
        payment_information_data_with_error = {
            "client_wizard-current_step": "payment_information",
            "payment_information-member": "[{}] Second Member".format(pk),
            "payment_information-firstname": "",
            "payment_information-lastname": "",
            "payment_information-billing_payment_type": "check",
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
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'billing_payment_type' in response_error.content)
        self.assertTrue(b'facturation' in response_error.content)
        self.assertTrue(
            b'member has not a valid address'
            in response_error.content
        )

        # Data for the address_information step with errors.
        payment_information_data_with_error = {
            "client_wizard-current_step": "payment_information",
            "payment_information-member": "",
            "payment_information-firstname": "Third",
            "payment_information-lastname": "Member",
            "payment_information-billing_payment_type": "check",
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
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'street' in response_error.content)
        self.assertTrue(b'city' in response_error.content)
        self.assertTrue(b'postal_code' in response_error.content)
        self.assertTrue(b'This field is required' in response_error.content)

    def _test_payment_information_without_errors(self):
        # Data for the address_information step without errors.
        pk = Member.objects.get(firstname="First").id
        payment_information_data = {
            "client_wizard-current_step": "payment_information",
            "payment_information-member": "[{}] First Member".format(pk),
            "payment_information-firstname": "",
            "payment_information-lastname": "",
            "payment_information-billing_payment_type": "check",
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

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(b'billing_payment_type' not in response.content)
        self.assertTrue(b'facturation' not in response.content)
        self.assertTrue(
            b'member has not a valid address' not in response.content
        )
        # HTML from the next step
        self.assertTrue(b'status' in response.content)

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
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'status' in response_error.content)
        self.assertTrue(b'delivery_type' in response_error.content)
        self.assertTrue(b'meals_schedule' in response_error.content)

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

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(b'status' not in response.content)
        self.assertTrue(b'Delivery' not in response.content)
        self.assertTrue(b'Food preference' not in response.content)
        # HTML from the next step
        self.assertTrue(b'contact_type' in response.content)

    def _test_step_emergency_contact_with_errors(self):
        # Data for the address_information step with errors.
        emergency_contact_data_with_error = {
            "client_wizard-current_step": "emergency_contact",
            "emergency_contact-firstname": "",
            "emergency_contact-lastname": "",
            "emergency_contact-contact_type": "Home phone",
            "emergency_contact-contact_value": ""
        }

        # Send the data to the form.
        response_error = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "emergency_contact"}
            ),
            emergency_contact_data_with_error,
            follow=True
        )

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' in response_error.content)
        self.assertTrue(b'contact_type' in response_error.content)
        self.assertTrue(b'contact_value' in response_error.content)

    def _test_step_emergency_contact_without_errors(self):
        # Data for the address_information step without errors.
        pk = Member.objects.get(firstname="First").id
        emergency_contact_data = {
            "client_wizard-current_step": "emergency_contact",
            "emergency_contact-member": "[{}] First Member".format(pk),
            "emergency_contact-firstname": "Emergency",
            "emergency_contact-lastname": "User",
            "emergency_contact-contact_type": "Home phone",
            "emergency_contact-contact_value": "555-444-5555"
        }

        # Send the data to the form.
        response = self.client.post(
            reverse_lazy(
                'member:member_step',
                kwargs={'step': "emergency_contact"}
            ),
            emergency_contact_data,
            follow=True
        )

        # The response is the next step of the form with no errors messages.
        self.assertTrue(b'Required information' not in response.content)
        self.assertTrue(b'contact_type' not in response.content)
        self.assertTrue(b'contact_value' not in response.content)
        self.assertTrue(b'Clients' in response.content)
        self.assertRedirects(response, reverse('member:list'))


class MemberSearchTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        member = Member.objects.create(
            firstname='Katrina', lastname='Heide')
        Contact.objects.create(
            type='Home phone', value='514-456-7890', member=member)

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
        self.assertEqual(scheduled_change_start.linked_scheduled_status, None)
        self.assertEqual(scheduled_change_end.operation_status,
                         ClientScheduledStatus.TOBEPROCESSED)
        self.assertEqual(scheduled_change_end.status_from, Client.PAUSED)
        self.assertEqual(scheduled_change_end.status_to,
                         self.active_client.status)
        self.assertEqual(scheduled_change_end.reason, 'Holidays')
        self.assertEqual(scheduled_change_end.linked_scheduled_status,
                         scheduled_change_start)

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
        self.assertEqual(scheduled_change.linked_scheduled_status, None)


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
            'street': '111 rue Roy',
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
            'referral_reason': 'Testing referral reason',
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
            'billing_payment_type': 'check',
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
            'billing_payment_type': 'check',
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
            'postal_code': None,
            'member': '[{}] {} {}'.format(
                payment.id,
                payment.firstname,
                payment.lastname
            ),
            'same_as_client': False,
            'billing_payment_type': 'check',
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
        self.assertEqual(client.status, 'A')
        self.assertEqual(client.delivery_type, "O")


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
            'member': '[0] Not Valid',
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertFalse(form.is_valid())
        data.update({
            'firstname': None,
            'lastname': None,
            'member': '[{}] {} {}'.format(
                client.emergency_contact.id,
                client.emergency_contact.firstname,
                client.emergency_contact.lastname
            ),
            'contact_type':
                client.emergency_contact.member_contact.first().type,
            'contact_value':
                client.emergency_contact.member_contact.first().value,
        })
        form = ClientEmergencyContactInformation(data=data)
        self.assertTrue(form.is_valid())

    def test_update_referent_information(self):
        """
        Test the update basic information form.
        """
        client = ClientFactory()
        emergency = MemberFactory()
        # Load initial data related to the client
        data = load_initial_data(client)
        # Update some data
        data.update({
            'firstname': None,
            'lastname': None,
            'member': '[{}] {} {}'.format(
                emergency.id,
                emergency.firstname,
                emergency.lastname
            ),
            'contact_type':
                client.emergency_contact.member_contact.first().type,
            'contact_value':
                client.emergency_contact.member_contact.first().value,
        })

        # Login as admin
        self.login_as_admin()

        # Send the data to the form.
        self.client.post(
            reverse_lazy(
                'member:member_update_emergency_contact',
                kwargs={'pk': client.id}
            ),
            data,
            follow=True
        )

        # Reload client data as it should have been changed in the database
        client = Client.objects.get(id=client.id)
        self.assertEqual(client.emergency_contact.id, emergency.id)
        self.assertEqual(
            client.emergency_contact.firstname, emergency.firstname
        )
        self.assertEqual(client.emergency_contact.lastname, emergency.lastname)
