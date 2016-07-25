from django.core.management.base import BaseCommand
from member.factories import ClientFactory


class Command(BaseCommand):
    help = 'Creates a happy bunch of clients without orders'

    def handle(self, *args, **options):
        client = ClientFactory.create_batch(10)
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created client "%s"' % client
            )
        )
