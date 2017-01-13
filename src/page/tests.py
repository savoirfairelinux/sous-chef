from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse

from member.factories import RouteFactory, ClientFactory
from member.models import Client


class HomeViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='test'
        )

    def test_access_as_admin(self):
        """Only logged-in users can access the homepage"""
        self.client.login(
            username=self.admin.username,
            password="test"
        )
        result = self.client.get(
            reverse_lazy(
                'page:home'
            ),
            follow=False
        )
        self.assertEqual(result.status_code, 200)

    def test_as_anonymous(self):
        """User not logged-in can not access the homepage"""
        self.client.logout()
        result = self.client.get(
            reverse_lazy(
                'page:home'
            ),
            follow=True
        )
        self.assertRedirects(
            result,
            reverse('page:login') + '?next=/p/home',
            status_code=302
        )

    def test_route_client_counts(self):
        """
        On dashboard, routes shouly only include active and paused clients.
        """
        self.client.login(
            username=self.admin.username,
            password="test"
        )
        route = RouteFactory()
        counts = (
            (Client.PENDING, 1),
            (Client.ACTIVE, 2),
            (Client.PAUSED, 4),
            (Client.STOPNOCONTACT, 8),
            (Client.STOPCONTACT, 16),
            (Client.DECEASED, 32),
        )
        for status, count in counts:
            ClientFactory.create_batch(
                count,
                status=status,
                route=route
            )
        response = self.client.get(
            reverse_lazy(
                'page:home'
            ),
            follow=False
        )
        self.assertEqual(response.status_code, 200)
        routes = response.context['routes']
        self.assertEqual(routes[0][0], route.name)
        self.assertEqual(routes[0][1], 2 + 4)
