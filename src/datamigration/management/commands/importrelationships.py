from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from member.factories import ClientFactory, MemberFactory
from member.models import Client, Member, Route, Address, Contact, Referencing
import os
import csv
from sys import path
from datetime import date


class Command(BaseCommand):
    help = 'Data: import clients relationships from given csv file.'

    ROW_MID = 0
    ROW_RID = 1
    ROW_FIRSTNAME = 2
    ROW_LASTNAME = 3
    ROW_EMERGENCY = 4
    ROW_REFERENT = 5
    ROW_BILLTO = 6
    ROW_WORK_INFORMATION = 7
    ROW_RELATIONSHIP = 8
    ROW_REASON = 9
    ROW_STREET = 10
    ROW_APARTMENT = 11
    ROW_POSTAL_CODE = 12
    ROW_CITY = 13
    ROW_PHONE = 14

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=False,
            help='Import mock data instead of actual data',
        )

    def handle(self, *args, **options):
        if options['file']:
            file = 'mock_relationships.csv'
        else:
            file = 'clients_relationships.csv'

        with open(file) as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                try:
                    member = Member.objects.get(mid=row[self.ROW_MID])
                    client = Client.objects.get(member=member)

                    if row[self.ROW_FIRSTNAME] is not '':

                        relationship, created = Member.objects.update_or_create(
                            rid=row[self.ROW_RID], defaults={
                                "firstname": row[
                                    self.ROW_FIRSTNAME], "lastname": row[
                                    self.ROW_LASTNAME], })

                        if row[self.ROW_EMERGENCY] == '1':
                            self.stdout.write(
                                self.style.SUCCESS(
                                    'Added an emergency Relationship.'
                                ))
                            client.emergency_contact = relationship
                            client.emergency_contact_relationship = row[
                                self.ROW_RELATIONSHIP]
                        if row[self.ROW_BILLTO] == '1':
                            self.stdout.write(
                                self.style.SUCCESS(
                                    'Added a blling Relationship.'
                                ))
                            client.billing_member = relationship
                        if row[self.ROW_REFERENT] == '1':
                            referencing = Referencing.objects.create(
                                referent=relationship,
                                client=client,
                                referral_reason=row[self.ROW_REASON],
                                work_information=row[
                                    self.ROW_WORK_INFORMATION
                                ],
                                date=date.today(), )

                        client.save()

                except Member.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING('Non existing member'))
                except Client.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING('Non existing client'))
