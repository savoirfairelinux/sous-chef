from django.test import TestCase, Client
from member.models import Member, Client, Note, User, Address, Referencing
from member.models import Contact, Option, Client_option, Restriction
from member.models import Client_avoid_ingredient, Client_avoid_component
from meal.models import Restricted_item, Ingredient, Component
from datetime import date
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from order.models import Order


class MemberTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        member = Member.objects.create(
            firstname='Katrina', lastname='Heide')
        Contact.objects.create(
            type='Home phone', value='514-456-7890', member=member)

    def test_str_is_fullname(self):
        """A member must be listed using his/her fullname"""
        member = Member.objects.get(firstname='Katrina')
        str_member = str(member)
        self.assertEqual(str_member, 'Katrina Heide')

    def test_get_home_phone(self):
        """The home phone is properly stored"""
        katrina = Member.objects.get(firstname='Katrina')
        self.assertTrue(katrina.get_home_phone(), '514-456-7890')


class NoteTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Member.objects.create(firstname='Katrina',
                              lastname='Heide')
        User.objects.create(username="admin")

    def test_attach_note_to_member(self):
        """Create a note attached to a member"""
        member = Member.objects.get(firstname='Katrina')
        admin = User.objects.get(username='admin')
        note = Note.objects.create(member=member, author=admin)
        self.assertEqual(str(member), str(note.member))

    def test_mark_as_read(self):
        """Mark a note as read"""
        member = Member.objects.get(firstname='Katrina')
        admin = User.objects.get(username='admin')
        note = Note.objects.create(member=member, author=admin)
        self.assertFalse(note.is_read)
        note.mark_as_read()
        self.assertTrue(note.is_read)

    def test_str_includes_note(self):
        """An note listing must include the note text"""
        member = Member.objects.get(firstname='Katrina')
        admin = User.objects.get(username='admin')
        note = Note.objects.create(member=member, author=admin, note='x123y')
        self.assertTrue('x123y' in str(note))


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
            birthdate=date(1980, 4, 19))

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

    def test_acces_to_form(self):
        """Test if the form is accesible from its url"""
        self.client.login(
            username=self.admin.username,
            password=self.admin.password
        )
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

    def test_form_save_data(self):

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

        address_information_data = {
            "client_wizard-current_step": "address_information",
            "address_information-street": "555 rue clark",
            "address_information-apartment": "222",
            "address_information-city": "montreal",
            "address_information-postal_code": "H3C2C2",
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
            "dietary_restriction-delivery_schedule": "mon",
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
            self.client.post(
                reverse_lazy('member:member_step', kwargs={'step': step}),
                data,
                follow=True
            )

        member = Member.objects.get(firstname="User")

        # test_member_name:
        self.assertTrue(member.firstname, "User")
        self.assertTrue(member.lastname, "Testing")

        # test_home_phone_member:
        self.assertTrue(member.get_home_phone().value.startswith('555'))

        client = Client.objects.get(member=member)

        # test_client_alert:
        self.assertTrue(client.alert, "Testing alert message")

        # test_client_languages:
        self.assertTrue(client.language, "fr")

        # test_client_birthdate:
        self.assertTrue(client.birthdate, "1990-12-12")

        # test_client_gender:
        self.assertTrue(client.gender, "M")

        # test_client_contact_type:
        self.assertTrue(member.member_contact, "Home phone")

        # test_client_address:
        self.assertTrue(member.address.street, "555 rue clark")
        self.assertTrue(member.address.postal_code, "H3C2C2")
        self.assertTrue(member.address.apartment, "222")
        self.assertTrue(member.address.city, "montreal")

        # test client delivery type
        self.assertEqual(client.delivery_type, 'O')

        # test_referent_name:
        self.assertTrue(
            client.client_referent.first().referent.firstname,
            "Referent"
        )
        self.assertTrue(
            client.client_referent.first().referent.lastname,
            "Testing"
        )

        # test_referent_work_information:
        self.assertTrue(
            client.client_referent.first().work_information,
            "CLSC"
        )

        # test_referral_date(self):
        self.assertTrue(client.client_referent.first().date, "2012-12-12")

        # test_referral_reason:
        self.assertTrue(
            client.client_referent.first().referral_reason,
            "Testing referral reason"
        )

        # test_billing_name:
        self.assertTrue(client.billing_member.firstname, "Testing")
        self.assertTrue(client.billing_member.lastname, "Billing")

        #  test_billing_type:
        self.assertTrue(client.billing_payment_type, "check")

        #  test_billing_address:
        self.assertTrue(client.billing_member.address.city, "Montreal")
        self.assertTrue(client.billing_member.address.street, "111 rue clark")
        self.assertTrue(client.billing_member.address.postal_code, "H2C3G4")

        #  test_billing_rate_type:
        self.assertTrue(client.rate_type, 'default')

        #  test_emergency_contact_name:
        self.assertTrue(client.emergency_contact.firstname, "Emergency")
        self.assertTrue(client.emergency_contact.lastname, "User")

        #  test_emergency_contact_value:
        self.assertTrue(
            client.emergency_contact.get_home_phone,
            "555-444-5555"
        )

    def tear_down(self):
        self.client.logout()
