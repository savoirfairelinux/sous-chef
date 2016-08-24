from django.core.management.base import BaseCommand
from member.factories import ClientFactory
from member.models import Client, ClientScheduledStatus, Member
from django.core.management import call_command
import os
from datetime import date, datetime
from sys import path


class Command(BaseCommand):
    help = 'Process scheduled status changes, \
        queued in «member_ClientScheduledStatus» table.'

    def handle(self, *args, **options):
        # List all change not processed, and older or equal to now
        changes = ClientScheduledStatus.objects.filter(
            operation_status=ClientScheduledStatus.TOBEPROCESSED
        ).filter(
            change_date__lte=date.today()
        )

        # For each change to be processed,
        for scheduled_change in changes:
            if scheduled_change.process():
                suc_msg = ": client «{}» status updated from {} to {}.".format(
                    scheduled_change.client.member,
                    scheduled_change.get_status_from_display(),
                    scheduled_change.get_status_to_display()
                )
                self.stdout.write(self.style.SUCCESS(
                    str(datetime.now()) + suc_msg))
            # If not, mark change as processed with error
            else:
                err_msg = ': client «{}» status not updated.'.format(
                    scheduled_change.client.member
                )
                err_msg += ' Current status is «{}», should be «{}».'.format(
                    scheduled_change.client.get_status_display(),
                    scheduled_change.get_status_from_display()
                )
                self.stdout.write(self.style.ERROR(
                    str(datetime.now()) + err_msg))
