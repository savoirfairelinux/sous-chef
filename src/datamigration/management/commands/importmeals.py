from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from member.factories import ClientFactory, MemberFactory
from member.models import Client, Member, Route, Address, Contact, Referencing
import os
import csv
import json
from sys import path
from datetime import date


class Command(BaseCommand):
    help = 'Data: import clients relationships from given csv file.'

    ROW_MID=0
    ROW_MEALS_SCHEDULE=1
    ROW_MON=2
    ROW_TUE=3
    ROW_WED=4
    ROW_THU=5
    ROW_FRI=6
    ROW_SAT=7

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=False,
            help='Import mock data instead of actual data',
        )

    def handle(self, *args, **options):
        if options['file']:
            file = 'mock_meals.csv'
        else:
            file = 'clients_meals.csv'

        with open(file) as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                try:
                    member = Member.objects.get(mid=row[self.ROW_MID])
                    client = Client.objects.get(member=member)
                    prefs = {}

                    days = [self.ROW_MON, self.ROW_TUE, self.ROW_WED, self.ROW_THU, self.ROW_FRI, self.ROW_SAT]
                    meals_schedule = []

                    for day in days:
                        if row[day] != "":
                            meals_schedule.append(row[day])
                            prefs[row[day]] = ''

                    client.set_meals_schedule(meals_schedule)
                    client.meal_default_week = json.dumps(prefs)
                    client.save()

                except Member.DoesNotExist:
                    self.stdout.write(self.style.WARNING('Non existing member'))
                except Client.DoesNotExist:
                    self.stdout.write(self.style.WARNING('Non existing client'))
