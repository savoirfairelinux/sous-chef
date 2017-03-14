import importlib
import itertools
from django.test import TestCase
from note.models import Note, NotePriority, NoteCategory
from note.factories import NoteFactory
from django.contrib.auth.models import User
from member.factories import ClientFactory, RouteFactory
from django.urls import reverse
from django.utils import timezone
from sous_chef.tests import TestMixin as SousChefTestMixin


class NoteTestCase(TestCase):

    fixtures = ['routes.json']

    @classmethod
    def setUpTestData(cls):
        cls.clients = ClientFactory()
        cls.admin = User.objects.create_superuser(
            username='admin', email='testadmin@example.com',
            password='test1234')
        cls.note = NoteFactory.create(
            client=cls.clients,
            author=cls.admin,
            priority=NotePriority.objects.get(
                pk=NotePriority.DEFAULT_PRIORITY_ID
            ),
            category=NoteCategory.objects.get(
                pk=NoteCategory.DEFAULT_CATEGORY_ID
            )
        )

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


class NoteAddTestCase(NoteTestCase):

    def setUp(self):
        self.client.force_login(
            self.admin, 'django.contrib.auth.backends.ModelBackend')

    def test_create_set_fields(self):
        """
        Test if author, date, is_read are correctly set.
        """
        time_1 = timezone.now()
        response = self.client.post(reverse('note:note_add'), {
            'note': "test note TEST_PHRASE",
            "client": ClientFactory().pk,
            "priority": '1',
            "category": '1'
        }, follow=False)
        time_2 = timezone.now()
        self.assertEqual(response.status_code, 302)  # successful creation
        note = Note.objects.get(note__contains="TEST_PHRASE")
        self.assertEqual(note.author, self.admin)
        self.assertEqual(note.is_read, False)
        self.assertTrue(time_1 <= note.date <= time_2)

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('note:note_add')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 302)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('note:note_add')
        # Run
        response = self.client.post(url, {
            'note': "test note TEST_PHRASE",
            "client": ClientFactory().pk,
            "priority": '1'
        }, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)


class ClientNoteAddTestCase(NoteTestCase):

    def setUp(self):
        self.client.force_login(
            self.admin, 'django.contrib.auth.backends.ModelBackend',)

    def test_get_with_client_pk(self):
        client = ClientFactory()
        response = self.client.get(reverse(
            'member:client_notes_add',
            kwargs={'pk': client.pk}
        ))
        self.assertEqual(response.status_code, 200)
        content = str(response.content, encoding=response.charset)
        self.assertIn(str(client.pk), content)
        self.assertIn(client.member.firstname, content)
        self.assertIn(client.member.lastname, content)

    def test_redirects_users_who_do_not_have_edit_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_notes_add', kwargs={'pk': client.pk})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 302)

    def test_allow_access_to_users_with_edit_permission(self):
        # Setup
        user = User.objects.create_superuser(
            username='foo', email='foo@example.com', password='secure')
        user.save()
        self.client.login(username='foo', password='secure')
        client = ClientFactory()
        url = reverse('member:client_notes_add', kwargs={'pk': client.pk})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


class RedirectAnonymousUserTestCase(SousChefTestMixin, TestCase):

    fixtures = ['routes.json']

    def test_anonymous_user_gets_redirect_to_login_page(self):
        check = self.assertRedirectsWithAllMethods
        check(reverse('note:note_list'))
        check(reverse('note:read', kwargs={'id': 1}))
        check(reverse('note:unread', kwargs={'id': 1}))
        check(reverse('note:note_add'))
        check(reverse('note:batch_toggle'))


class NoteListViewTestCase(SousChefTestMixin, TestCase):
    fixtures = ['routes.json']

    def test_redirects_users_who_do_not_have_read_permission(self):
        # Setup
        User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        self.client.login(username='foo', password='secure')
        url = reverse('note:note_list')
        # Run & check
        self.assertRedirectsWithAllMethods(url)

    def test_allow_access_to_users_with_read_permission(self):
        # Setup
        user = User.objects.create_user(
            username='foo', email='foo@example.com', password='secure')
        user.is_staff = True
        user.save()
        self.client.login(username='foo', password='secure')
        url = reverse('note:note_list')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_search_by_name(self):
        """
        Search text should be contained by either firstname or
        lastname.
        """
        client1 = ClientFactory(
            member__firstname='tessst',
            member__lastname='woooo'
        )
        client2 = ClientFactory(
            member__firstname='woooo',
            member__lastname='tessst'
        )
        client3 = ClientFactory(
            member__firstname='woooo',
            member__lastname='woooo'
        )
        note1a = NoteFactory(client=client1)
        note1b = NoteFactory(client=client1)
        note2a = NoteFactory(client=client2)
        note2b = NoteFactory(client=client2)
        note3a = NoteFactory(client=client3)
        note3b = NoteFactory(client=client3)

        self.force_login()
        url = reverse('note:note_list')
        response = self.client.get(
            url,
            {'name': 'esss'}
        )
        self.assertEqual(response.status_code, 200)
        notes = response.context['notes']
        self.assertIn(note1a, notes)
        self.assertIn(note1b, notes)
        self.assertIn(note2a, notes)
        self.assertIn(note2b, notes)
        self.assertNotIn(note3a, notes)
        self.assertNotIn(note3b, notes)


class NoteBatchToggleViewTestCase(SousChefTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        r = RouteFactory()  # prerequisite
        cls.unread_notes = NoteFactory.create_batch(10, is_read=False)
        cls.read_notes = NoteFactory.create_batch(10, is_read=True)

    def test_toggle(self):
        self.force_login()
        response = self.client.post(
            reverse('note:batch_toggle'),
            {'note': list(map(
                lambda n: n.id,
                itertools.chain(self.unread_notes, self.read_notes)
            ))},
            redirect=False
        )
        self.assertEqual(response.status_code, 302)  # should redirect

        # Refetch
        for n in self.unread_notes:
            n.refresh_from_db()
            self.assertTrue(n.is_read)
        for n in self.read_notes:
            n.refresh_from_db()
            self.assertFalse(n.is_read)
