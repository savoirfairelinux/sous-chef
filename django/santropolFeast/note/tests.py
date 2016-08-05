from django.test import TestCase
from member.models import Member, Client
from note.models import Note
from note.factories import NoteFactory
from django.contrib.auth.models import User
from member.factories import ClientFactory

# Create your tests here.


class NoteTestCase(TestCase):

    fixtures = ['routes.json']

    def setUp(self):
        self.client = ClientFactory()
        self.admin = User.objects.create(username="admin")
        self.note = NoteFactory.create(client=self.client, author=self.admin)

    def test_attach_note_to_member(self):
        """Create a note attached to a member"""
        note = self.note
        self.assertEqual(self.client, note.client)
        self.assertEqual(self.admin, note.author)

    def test_mark_as_read(self):
        """Mark a note as read"""
        note = self.note
        self.assertFalse(note.is_read)
        note.mark_as_read()
        self.assertTrue(note.is_read)

    def test_mark_as_unread(self):
        """Mark a note as unread"""
        note = self.note
        note.mark_as_read()
        self.assertTrue(note.is_read)
        note.mark_as_unread()
        self.assertFalse(note.is_read)

    def test_str_includes_note(self):
        """An note listing must include the note text"""
        note = Note.objects.create(
            client=self.client,
            author=self.admin,
            note='x123y'
        )
        self.assertTrue('x123y' in note.note)
