from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from member.models import Client, Member, Route
import os
import csv
from sys import path
from datetime import date


class Command(BaseCommand):
    help = 'Data: import clients from given csv file.'

    ROW_MID = 0
    ROW_FIRSTNAME = 1
    ROW_LASTNAME = 2
    ROW_BIRTHDATE = 3
    ROW_STATUS = 4
    ROW_CREATED = 5
    ROW_GENDER = 6
    ROW_LANG = 7
    ROW_PAYSCALE = 8
    ROW_ALERT = 9
    ROW_DELIVERY_NOTES = 10
    ROW_DELIVERY_TYPE = 11
    ROW_ROUTE = 12

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=False,
            help='Import mock data instead of actual data',
        )

    def handle(self, *args, **options):
        # Load fixtures for the routes
        fixture_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '../fixtures')
        )
        fixture_filename = 'routes.json'
        fixture_file = os.path.join(fixture_dir, fixture_filename)
        call_command('loaddata', fixture_filename)

        if options['file']:
            file = 'mock_clients.csv'
        else:
            file = 'clients.csv'

        with open(file) as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:

                row_created = row[
                    self.ROW_CREATED] if row[
                    self.ROW_CREATED] != '' else date.today()

                member, created = Member.objects.update_or_create(
                    mid=row[self.ROW_MID],
                    defaults={
                        "firstname": row[self.ROW_FIRSTNAME],
                        "lastname": row[self.ROW_LASTNAME],
                        "updated_at": row_created,
                    }
                )

                route, created = Route.objects.get_or_create(
                    name=row[self.ROW_ROUTE]
                )
                if created:
                    err_msg = "A new route has been created."
                    self.stdout.write(self.style.WARNING(err_msg))
                    route = None

                client, created = Client.objects.update_or_create(
                    member=member,
                    defaults={
                        "billing_member": member,
                        "birthdate": row[self.ROW_BIRTHDATE],
                        "status": row[self.ROW_STATUS],
                        "gender": row[self.ROW_GENDER],
                        "alert": row[self.ROW_ALERT],
                        "delivery_type": row[self.ROW_DELIVERY_TYPE],
                        "delivery_note": row[self.ROW_DELIVERY_NOTES],
                        "route": route,
                        'language': row[self.ROW_LANG],
                    }
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        '{} successfully {}.'.format(
                            client,
                            'created' if created else 'updated')))

                # Override creation date
                client.member.created_at = row_created
                client.member.save()

                # Add Client option meals_schedule
                # client.set_meals_schedule([])
