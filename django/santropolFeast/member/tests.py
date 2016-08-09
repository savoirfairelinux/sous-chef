from django.test import TestCase, Client
from member.models import Member, Client, User, Address, Referencing
from member.models import Contact, Option, Client_option, Restriction, Route
from member.models import Client_avoid_ingredient, Client_avoid_component
from meal.models import Restricted_item, Ingredient, Component
from datetime import date
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from order.models import Order
from member.factories import RouteFactory


class MemberEmptyContact(TestCase):

    @classmethod
    def setUpTestData(cls):
        member = Member.objects.create(
            firstname='Katrina', lastname='Heide')

    def test_home_phone_blank(self):
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.home_phone, "")

    def test_cell_phone_blank(self):
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.cell_phone, "")

    def test_work_phone_blank(self):
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.work_phone, "")

    def test_email_blank(self):
        member = Member.objects.get(firstname="Katrina")
        self.assertEqual(member.email, "")


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
            birthdate=date(1980, 4, 19),
            meal_default_week={'monday_size': 'L',
                               'monday_main_dish_quantity': 1
                               })

        Order.objects.create(
            creation_date=date(2016, 5, 5),
            delivery_date=date(2016, 5, 10),
            status='B', client=client,
        )

    def test_str_is_fullname(self):
        """A client must be listed using his/her fullname"""
        member = Member.objects.get(firstname='Angela')
        client = Client.objects.get(member=member)
        self.assertTrue(member.firstname in str(client))
        self.assertTrue(member.lastname in str(client))

    def test_age(self):
        """The age on given date is properly computed"""
        member = Member.objects.get(firstname='Angela')
        angela = Client.objects.get(member=member)
        self.assertEqual(angela.age, 36)

    def test_default(self):
        """Default values must be properly set on client creation"""
        member = Member.objects.get(firstname='Angela')
        angela = Client.objects.get(member=member)
        # Language: French
        self.assertEqual(angela.language, 'fr')
        # Status: Pending
        self.assertEqual(angela.status, 'D')
        # Gender: empty
        self.assertEqual(angela.gender, 'U')
        # Delivery type: Ongoing
        self.assertEqual(angela.delivery_type, 'O')

    def test_orders(self):
        """Orders of a given client must be available as a model property"""
        member = Member.objects.get(firstname='Angela')
        angela = Client.objects.get(member=member)
        self.assertEqual(angela.orders.count(), 1)
        self.assertEqual(angela.orders.first().creation_date, date(2016, 5, 5))

    def test_meal_default(self):
        member = Member.objects.get(firstname='Angela')
        angela = Client.objects.get(member=member)

        # monday_size = 'L'
        self.assertEqual(angela.meal_default_week['monday_size'], 'L')

        # monday_main_dish_quantity = 1
        self.assertEqual(
            angela.meal_default_week['monday_main_dish_quantity'], 1
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
        option = Option.objects.create(
            name='PUREE ALL', option_group='preparation')
        Client_option.objects.create(client=client, option=option)

    def test_str_includes_all_names(self):
        """A Client_option's string representation includes the name
        of the client and the name of the option.
        """
        member = Member.objects.get(firstname='Angela')
        client = Client.objects.get(member=member)
        name = 'PUREE ALL'
        option = Option.objects.get(name=name)
        client_option = Client_option.objects.get(
            client=client, option=option)
        self.assertTrue(client.member.firstname in str(client_option))
        self.assertTrue(client.member.lastname in str(client_option))
        self.assertTrue(option.name in str(client_option))


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
            "basic_information-contact_type": "Home phone",
            "basic_information-contact_value": "555-555-5555",
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
            "dietary_restriction-delivery_schedule": "monday",
            "dietary_restriction-meal_default": "1",
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

        self._test_client_detail_view_all_different_members(client)

    def _test_assert_member_info_all_different_members(self, member):
        # test firstname and lastname
        self.assertEqual(member.firstname, "User")
        self.assertEqual(member.lastname, "Testing")

        # test_home_phone_member:
        self.assertTrue(member.home_phone.startswith('555'))

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

    def _test_client_detail_view_all_different_members(self, client):
        response = self.client.get(
            reverse_lazy('member:view', kwargs={'pk': client.id})
        )

        self.assertTrue(b"User" in response.content)
        self.assertTrue(b"Testing" in response.content)
        self.assertTrue(b"Home phone" in response.content)
        self.assertTrue(b"555 rue clark" in response.content)
        self.assertTrue(b"H3C2C2" in response.content)
        self.assertTrue(b"montreal" in response.content)
        self.assertTrue(b"Testing alert message" in response.content)
        self.assertTrue(b"Testing referral reason" in response.content)
        self.assertTrue(b"555-444-5555" in response.content)

    def test_form_save_data_same_members(self):
        basic_information_data = {
            "client_wizard-current_step": "basic_information",
            "basic_information-firstname": "Same",
            "basic_information-lastname": "User",
            "basic_information-language": "fr",
            "basic_information-gender": "M",
            "basic_information-birthdate": "1986-06-06",
            "basic_information-contact_type": "Home phone",
            "basic_information-contact_value": "514-868-8686",
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
            "dietary_restriction-delivery_schedule": "monday",
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
            reverse_lazy('member:view', kwargs={'pk': client.id})
        )
        self.assertTrue(b"User" in response.content)
        self.assertTrue(b"Same" in response.content)
        self.assertTrue(b"Home phone" in response.content)
        self.assertTrue(b"8686 rue clark" in response.content)
        self.assertTrue(b"H8C6C8" in response.content)
        self.assertTrue(b"Montreal" in response.content)
        self.assertTrue(b"Testing alert message" in response.content)
        self.assertTrue(b"Testing referral reason" in response.content)
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
            "basic_information-contact_type": "Home phone",
            "basic_information-contact_value": "",
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
        self.assertTrue(b'contact_value' in error_response.content)
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
            "basic_information-contact_type": "Home phone",
            "basic_information-contact_value": "555-555-5555",
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
            "dietary_restriction-delivery_schedule": "",
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
        self.assertTrue(b'delivery_schedule' in response_error.content)

    def _test_step_dietary_restriction_without_errors(self):
        # Data for the address_information step without errors.
        restriction_information_data = {
            "client_wizard-current_step": "dietary_restriction",
            "dietary_restriction-status": "on",
            "dietary_restriction-delivery_type": "O",
            "dietary_restriction-delivery_schedule": "monday",
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
