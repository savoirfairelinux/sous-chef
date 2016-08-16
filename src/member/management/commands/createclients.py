from django.core.management.base import BaseCommand
from member.factories import ClientFactory
from django.core.management import call_command
import os
from sys import path


class Command(BaseCommand):
    help = 'Creates a happy bunch of clients without orders'

    def handle(self, *args, **options):
        # Load fixtures for the routes
        fixture_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../fixtures')
        )
        fixture_filename = 'routes.json'
        fixture_file = os.path.join(fixture_dir, fixture_filename)
        call_command('loaddata', fixture_filename)

        client = ClientFactory.create_batch(10)
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created client "%s"' % client
            )
        )
