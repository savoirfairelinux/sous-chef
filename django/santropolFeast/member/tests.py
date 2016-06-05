from django.test import TestCase
from member.models import Member, Client, Note, User, Address, Referencing
from member.models import Contact
from datetime import date


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
        self.assertEqual(str(member), 'Katrina Heide')

    def test_get_home_phone(self):
        """The home phone is properly stored"""
        katrina = Member.objects.get(firstname='Katrina')
        self.assertTrue(katrina.get_home_phone().value.startswith('514'))


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
        member = Member.objects.create(
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

    def test_str_is_fullname(self):
        """A client must be listed using his/her fullname"""
        member = Member.objects.get(firstname='Angela')
        client = Client.objects.get(member=member)
        self.assertTrue(member.firstname in str(client))
        self.assertTrue(member.lastname in str(client))

    def test_age_on_date(self):
        """The age on given date is properly computed"""
        member = Member.objects.get(firstname='Angela')
        angela = Client.objects.get(member=member)
        self.assertEqual(angela.age_on_date(date(2016, 4, 19)), 36)
        self.assertEqual(angela.age_on_date(date(1950, 4, 19)), 0)
        self.assertEqual(angela.age_on_date(angela.birthdate), 0)
