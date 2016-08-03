from django.core.management.base import BaseCommand
from member.factories import NoteFactory


class Command(BaseCommand):
    help = 'Creates notes related to members.'

    def handle(self, *args, **options):
        notes = NoteFactory.create_batch(20)
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created notes "%s"' % notes
            )
        )
