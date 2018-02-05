from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils.http import urlquote

METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS')


class TestMixin(object):

    def assertRedirectsWithAllMethods(self, url, methods=METHODS, **kwargs):
        """
        Test a URL with all HTTP methods, as not logged-in guests.
        """
        self.client.logout()
        for method in methods:
            response = getattr(self.client, method.lower())(url)
            self.assertRedirects(
                response,
                urlquote(settings.LOGIN_URL) + '?next=' + urlquote(url),
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
        self.client.force_login(
            admin, 'django.contrib.auth.backends.ModelBackend',)


class TestMigrations(TransactionTestCase):
    """
    https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    https://gist.github.com/blueyed/4fb0a807104551f103e6
    """
    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and " \
            "migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        # Reverse to the original migration
        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        raise NotImplementedError(
            "TestCase '{}' must define the method "
            "setUpBeforeMigration(self, apps)".format(type(self).__name__)
        )

    def tearDown(self):
        """
        In the end, ensure that the tested app has its latest migration.
        """
        call_command('migrate', self.app, verbosity=0)
