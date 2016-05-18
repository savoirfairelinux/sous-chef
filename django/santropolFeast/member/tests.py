from django.test import TestCase
from member.models import Member, Client, Note, User
from datetime import date


class MemberTestCase(TestCase):

    def setUp(self):
        Member.objects.create(firstname='Katrina',
                              lastname='Heide', birthdate=date(1980, 4, 19))

    def test_age_on_date(self):
        """The age on given date is properly computed"""
        katrina = Member.objects.get(firstname='Katrina')
        self.assertEqual(katrina.age_on_date(date(2016, 4, 19)), 36)
        self.assertEqual(katrina.age_on_date(date(1950, 4, 19)), 0)
        self.assertEqual(katrina.age_on_date(katrina.birthdate), 0)

    def test_str_is_fullname(self):
        """A member must be listed using his/her fullname"""
        member = Member.objects.get(firstname='Katrina')
        self.assertEqual(str(member), 'Katrina Heide')


class NoteTestCase(TestCase):

    def setUp(self):
        Member.objects.create(firstname='Katrina',
                              lastname='Heide', birthdate=date(1980, 4, 1))
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
