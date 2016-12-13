from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from member.factories import ClientFactory, MemberFactory
from member.models import Client, Member, Route, Address, Contact, Referencing
from member.models import Option, Client_option, Client_avoid_ingredient
from note.models import Note
from meal.models import Ingredient
import os
import csv
import json
from sys import path
from datetime import date


class Command(BaseCommand):
    help = 'Data: import clients relationships from given csv file.'

    ROW_MID = 0
    ROW_MON = 1
    ROW_TUE = 2
    ROW_WED = 3
    ROW_THU = 4
    ROW_FRI = 5
    ROW_SAT = 6
    ROW_FOOD_PREP_PUREE = 7
    ROW_FOOD_PREP_CUT = 8
    ROW_MLABEL = 9
    ROW_ING_BEEF = 10

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

        food_prep_puree = Option.objects.get(
            name='Puree all'
        )
        food_prep_cut = Option.objects.get(
            name='Cut up meat'
        )

        ingredients = Ingredient.objects.all()
        beef = Ingredient.objects.all().filter(name__icontains='beef')

        with open(file) as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                try:
                    member = Member.objects.get(mid=row[self.ROW_MID])
                    client = Client.objects.get(member=member)
                    days = [
                        self.ROW_MON,
                        self.ROW_TUE,
                        self.ROW_WED,
                        self.ROW_THU,
                        self.ROW_FRI,
                        self.ROW_SAT]
                    meals_schedule = []
                    prefs = {}

                    for day in days:
                        if row[day] != "":
                            meals_schedule.append(row[day])
                            prefs['size_' + row[day]] = 'R'
                            prefs['main_dish_' + row[day] + '_quantity'] = 1
                            prefs['compote_' + row[day] + '_quantity'] = 0
                            prefs['dessert_' + row[day] + '_quantity'] = 1
                            prefs['fruit_salad_' + row[day] + '_quantity'] = 0
                            prefs['green_salad_' + row[day] + '_quantity'] = 1
                            prefs['pudding_' + row[day] + '_quantity'] = 0

                    client.set_meals_schedule(meals_schedule)
                    client.meal_default_week = prefs
                    client.save()

                    # Food preparation
                    if row[self.ROW_FOOD_PREP_CUT] == '1':
                        Client_option.objects.create(
                            client=client,
                            option=food_prep_cut
                        )
                    if row[self.ROW_FOOD_PREP_PUREE] == '1':
                        Client_option.objects.create(
                            client=client,
                            option=food_prep_puree
                        )

                    # Add a note that contains the old meal label
                    if row[self.ROW_MLABEL] != "":
                        note = Note(
                            note=row[self.ROW_MLABEL],
                            author=None,
                            client=client,
                        )
                        note.save()

                except Member.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING('Non existing member'))
                except Client.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING('Non existing client'))
