from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse


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
