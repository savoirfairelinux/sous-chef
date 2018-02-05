from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from member.factories import ClientFactory, MemberFactory
from member.models import Client, Member, Route, Address, Contact
from member.models import EMAIL, HOME, CELL, WORK
import os
import csv
from sys import path


class Command(BaseCommand):
    help = 'Data: import clients from given csv file.'

    ROW_RID = 0
    ROW_ADDRESS1 = 3
    ROW_APARTMENT = 4
    ROW_CITY = 5
    ROW_POSTAL_CODE = 6
    ROW_HOME_PHONE = 7
    ROW_CELL_PHONE = 8
    ROW_WORK_PHONE = 9
    ROW_EXT = 10
    ROW_EMAIL = 11

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=False,
            help='Import mock data instead of actual data',
        )

    def handle(self, *args, **options):
        if options['file']:
            file = 'mock_contactaddresses.csv'
        else:
            file = 'contact_address.csv'

        with open(file) as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                try:
                    member = Member.objects.get(rid=row[self.ROW_RID])

                    address = Address.objects.create(
                        street=row[self.ROW_ADDRESS1],
                        apartment=row[self.ROW_APARTMENT],
                        city=row[self.ROW_CITY],
                        postal_code=row[self.ROW_POSTAL_CODE],
                    )

                    member.address = address
                    member.save()

                    contacts = Contact.objects.filter(member=member)
                    contacts.delete()

                    if row[self.ROW_HOME_PHONE] is not '' \
                            and len(row[self.ROW_HOME_PHONE]) >= 7:
                        contact = Contact.objects.create(
                            type=HOME,
                            value=row[self.ROW_HOME_PHONE],
                            member=member
                        )
                    if row[self.ROW_CELL_PHONE] is not ''\
                            and len(row[self.ROW_CELL_PHONE]) >= 7:
                        contact = Contact.objects.create(
                            type=CELL,
                            value=row[self.ROW_CELL_PHONE],
                            member=member
                        )

                    if row[self.ROW_WORK_PHONE] is not ''\
                            and len(row[self.ROW_WORK_PHONE]) >= 7:
                        work = row[self.ROW_WORK_PHONE]
                        if row[self.ROW_EXT] is not '':
                            work += '  #' + row[self.ROW_EXT]

                        contact = Contact.objects.create(
                            type=WORK,
                            value=work,
                            member=member
                        )
                    if row[self.ROW_EMAIL] is not '':
                        contact = Contact.objects.create(
                            type=EMAIL,
                            value=row[self.ROW_EMAIL],
                            member=member
                        )

                except Member.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING('Non existing member'))
