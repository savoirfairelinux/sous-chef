from django.conf import settings
from django.contrib.auth.models import User

METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS')


class TestMixin(object):

    def assertRedirectsWithAllMethods(self, url, methods=METHODS, **kwargs):
        """
        Test a URL with all HTTP methods.
        """
        self.client.logout()
        for method in methods:
            response = getattr(self.client, method.lower())(url)
            self.assertRedirects(
                response,
                settings.LOGIN_URL + '?next=' + url,
                status_code=302,
                msg_prefix="{0} {1} ".format(method, url),
                **kwargs
            )

    def force_login(self, role="admin"):
        """
        Create administrator and force login for testing purposes.

        Possible to extend `role` in the future.
        """
        if User.objects.filter(is_superuser=True).exists():
            admin = User.objects.filter(is_superuser=True).first()
        else:
            admin = User.objects.create_superuser(
                username='testadmin',
                email='testadmin@example.com',
                password='test1234'
            )
        self.client.force_login(admin, 'django.contrib.auth.backends.ModelBackend',)
