from django.test import TestCase
from member.models import Member
from datetime import date


class MemberTestCase(TestCase):

    def setUp(self):
        Member.objects.create(firstname='Katrina', birthdate=date(1980, 4, 19))

    def test_age_on_date(self):
        """The age on given date is properly computed"""
        katrina = Member.objects.get(firstname='Katrina')
        self.assertEqual(katrina.age_on_date(date(2016, 4, 19)), 36)
        self.assertEqual(katrina.age_on_date(date(1950, 4, 19)), 0)
        self.assertEqual(katrina.age_on_date(katrina.birthdate), 0)
