from django.core.management.base import BaseCommand
from member.factories import ClientFactory
from member.models import Client, Client_scheduled_status, Member
from django.core.management import call_command
import os
import datetime
from sys import path


class Command(BaseCommand):
    help = 'Process scheduled status changes, queued in «member_client_scheduled_status» table.'

    def handle(self, *args, **options):
        # List all change not processed, and older or equal to now
        changes = Client_scheduled_status.objects.filter(
            operation_status = Client_scheduled_status.TOBEPROCESSED
        ).filter(
            change_date__lte = datetime.date.today()
        )

        # For each change to be processed,
        for status_change in changes:
            client = status_change.client
            # If client current status correspond with operation status_from,
            # let's operate modification and mark change as processed
            if client.status == status_change.status_from:
                client.status = status_change.status_to
                client.save()
                status_change.operation_status = Client_scheduled_status.PROCESSED
                status_change.save()
                self.stdout.write(self.style.SUCCESS("Client «{}» status updated from {} to {}.".format(
                    client.member, status_change.status_from, status_change.status_to
                )))
            # If not, mark change as processed with error
            else:
                status_change.operation_status = Client_scheduled_status.ERROR
                status_change.save()
                self.stdout.write(self.style.ERROR("Client «{}» status not updated. Current status is {}, but it should be {}.".format(
                    client.member, client.status, status_change.status_from
                )))
