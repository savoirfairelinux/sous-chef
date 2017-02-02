# coding=utf-8
import factory
import random

from member.models import (
    Member, Client, Contact, Route, Address, Referencing,
    EmergencyContact, GENDER_CHOICES, PAYMENT_TYPE,
    DELIVERY_TYPE, DAYS_OF_WEEK, RATE_TYPE,
    ClientScheduledStatus
)
from meal.models import COMPONENT_GROUP_CHOICES


class AddressFactory (factory.DjangoModelFactory):

    class Meta:
        model = Address

    street = factory.Faker('street_address')
    apartment = factory.Faker('random_number')
    city = 'Montreal'
    postal_code = factory.Faker('postalcode', locale="en_CA")
    latitude = "75.048439"
    longitude = "40.232434"


class MemberFactory (factory.DjangoModelFactory):

    class Meta:
        model = Member

    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')

    address = factory.SubFactory(AddressFactory)
    work_information = factory.Faker('company')
    contact = factory.RelatedFactory(
        'member.factories.ContactFactory',
        'member'
    )


class RouteFactory(factory.DjangoModelFactory):

    class Meta:
        model = Route

    name = factory.Faker('name')


def generate_json():
    json = {}
    for day, translation in DAYS_OF_WEEK:
        for meal, Meal in COMPONENT_GROUP_CHOICES:
            json['{}_{}_quantity'.format(meal, day)] = random.choice([0, 1])
    return json


class ClientFactory (factory.DjangoModelFactory):

    class Meta:
        model = Client

    member = factory.SubFactory(MemberFactory)
    billing_member = member
    billing_payment_type = factory.LazyAttribute(
        lambda x: random.choice(PAYMENT_TYPE)[0]
    )
    rate_type = factory.LazyAttribute(
        lambda x: random.choice(RATE_TYPE)[0]
    )
    member = member
    status = factory.LazyAttribute(
        lambda x: random.choice(
            Client.CLIENT_STATUS)[0]
    )
    language = factory.LazyAttribute(
        lambda x: random.choice(
            Client.LANGUAGES)[0]
    )
    alert = factory.Faker('sentence')
    delivery_type = factory.LazyAttribute(
        lambda x: random.choice(DELIVERY_TYPE)[0]
    )
    gender = factory.LazyAttribute(
        lambda x: random.choice(GENDER_CHOICES)[0]
    )
    birthdate = factory.Faker('date')
    route = factory.LazyAttribute(
        lambda x: random.choice(Route.objects.all())
    )

    delivery_note = factory.Faker('sentence')

    meal_default_week = factory.LazyAttribute(lambda x: generate_json())

    referencing = factory.RelatedFactory(
        'member.factories.ReferencingFactory',
        'client'
    )


class EmergencyContactFactory(factory.DjangoModelFactory):
    class Meta:
        model = EmergencyContact

    client = factory.SubFactory(ClientFactory)
    member = factory.SubFactory(MemberFactory)
    relationship = factory.LazyAttribute(
        lambda x: random.choice(['friends', 'family', 'coworkers'])
    )


class ReferencingFactory(factory.DjangoModelFactory):

    class Meta:
        model = Referencing

    referent = factory.SubFactory(MemberFactory)

    client = factory.SubFactory(ClientFactory)

    referral_reason = factory.Faker('sentence')

    date = factory.Faker('date')


class ContactFactory (factory.DjangoModelFactory):

    class Meta:
        model = Contact

    type = 'Home phone'
    value = factory.Sequence(lambda n: '514-555-%04d' % n)
    member = factory.SubFactory(MemberFactory)


class ClientScheduledStatusFactory(factory.DjangoModelFactory):

    class Meta:
        model = ClientScheduledStatus

    client = factory.SubFactory(ClientFactory)
    status_from = factory.LazyAttribute(
        lambda x: random.choice(
            Client.CLIENT_STATUS)[0]
    )
    status_to = factory.LazyAttribute(
        lambda x: random.choice(
            Client.CLIENT_STATUS)[0]
    )
    reason = factory.Faker('sentence')
    change_date = factory.Faker('date')
    change_state = factory.LazyAttribute(
        lambda x: random.choice(
            ClientScheduledStatus.CHANGE_STATUS)[0]
    )
    operation_status = ClientScheduledStatus.TOBEPROCESSED
