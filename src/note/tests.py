from django.test import TestCase
from note.models import Note
from note.factories import NoteFactory
from django.contrib.auth.models import User
from member.factories import ClientFactory
from django.core.urlresolvers import reverse


class NoteTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        cls.clients = ClientFactory()
        cls.admin = User.objects.create(username="admin")
        cls.note = NoteFactory.create(client=cls.clients, author=cls.admin)

    def test_attach_note_to_member(self):
        """Create a note attached to a member"""
        note = self.note
        self.assertEqual(self.clients, note.client)
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
            client=self.clients,
            author=self.admin,
            note='x123y'
        )
        self.assertTrue('x123y' in note.note)

    def test_anonymous_user_gets_redirected_to_login_page(self):
        self.client.logout()
        response = self.client.get('/note/')
        self.assertRedirects(
            response,
            reverse('page:login') + '?next=/note/',
            status_code=302
        )
