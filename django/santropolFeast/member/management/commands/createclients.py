import factory
from django.core.management.base import BaseCommand, CommandError
from member.models import Member as Member
from member.factories import MemberFactory, ClientFactory


class Command(BaseCommand):
    help = 'Creates a happy bunch of clients and orders'

    def handle(self, *args, **options):
        client = ClientFactory.create_batch(10)
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created client "%s"' %
                client))
