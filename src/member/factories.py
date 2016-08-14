# coding=utf-8
import factory
import random
from member.models import (
    Member, Client, Contact, Route, Address, Referencing,
    CONTACT_TYPE_CHOICES, GENDER_CHOICES, PAYMENT_TYPE,
    DELIVERY_TYPE, DAYS_OF_WEEK, RATE_TYPE,
    ClientScheduledStatus
)
from meal.models import COMPONENT_GROUP_CHOICES
from django.contrib.auth.models import User


class AddressFactory (factory.DjangoModelFactory):

    class Meta:
        model = Address

    street = factory.Faker('street_address')
    city = 'Montreal'
    postal_code = factory.Faker('postalcode')
    latitude = "75.0484393"
    longitude = "40.2324343"


class MemberFactory (factory.DjangoModelFactory):

    class Meta:
        model = Member

    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')

    address = factory.SubFactory(AddressFactory)
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
    emergency_contact = factory.SubFactory(MemberFactory)
    emergency_contact_relationship = factory.LazyAttribute(
        lambda x: random.choice(['friends', 'family', 'coworkers'])
    )
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

    meal_default_week = factory.LazyAttribute(lambda x: generate_json())

    referencing = factory.RelatedFactory(
        'member.factories.ReferencingFactory',
        'client'
    )


class ReferencingFactory(factory.DjangoModelFactory):

    class Meta:
        model = Referencing

    referent = factory.SubFactory(MemberFactory)

    client = factory.SubFactory(ClientFactory)

    referral_reason = factory.Faker('sentence')

    work_information = factory.Faker('company')

    date = factory.Faker('date')


class ContactFactory (factory.DjangoModelFactory):

    class Meta:
        model = Contact

    type = 'Home phone'
    value = factory.Faker('phone_number')
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
