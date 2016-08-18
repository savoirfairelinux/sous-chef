from django.core.management.base import BaseCommand
from member.factories import ClientFactory
from member.models import Client, ClientScheduledStatus, Member
from django.core.management import call_command
import os
import datetime
from sys import path


class Command(BaseCommand):
    help = 'Process scheduled status changes, \
        queued in «member_ClientScheduledStatus» table.'

    def handle(self, *args, **options):
        # List all change not processed, and older or equal to now
        changes = ClientScheduledStatus.objects.filter(
            operation_status=ClientScheduledStatus.TOBEPROCESSED
        ).filter(
            change_date__lte=datetime.date.today()
        )

        # For each change to be processed,
        for scheduled_change in changes:
            if scheduled_change.process():
                suc_msg = "Client «{}» status updated from {} to {}.".format(
                    scheduled_change.client.member,
                    scheduled_change.status_from,
                    scheduled_change.status_to
                )
                self.stdout.write(self.style.SUCCESS(suc_msg))
            # If not, mark change as processed with error
            else:
                err_msg = "Client «{}» status not updated. Current status \
                    is {}, but it should be {}.".format(
                    scheduled_change.client.member,
                    scheduled_change.client.status,
                    scheduled_change.status_from
                )
                self.stdout.write(self.style.ERROR(err_msg))
