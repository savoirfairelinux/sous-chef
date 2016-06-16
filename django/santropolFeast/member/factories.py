# coding=utf-8
import factory
import datetime
import random
from django.contrib.auth.models import User
from member.models import Member, Address, Contact, Client, PAYMENT_TYPE


class MemberFactory (factory.DjangoModelFactory):

    class Meta:
        model = Member

    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')


class AddressFactory (factory.DjangoModelFactory):

    class Meta:
        model = Address

    number = 5555
    street = "rue de la montagne"
    apartment = "234A"
    floor = 22
    city = "Montréal"
    postal_code = "H3C2C2"

    @classmethod
    def __init__(self, **kwargs):
        member = kwargs.pop("member", MemberFactory())
        address = super(AddressFactory, self).__init__(self, **kwargs)

        address.save()


class ClientFactory (factory.DjangoModelFactory):

    class Meta:
        model = Client

    billing_member = factory.SubFactory(MemberFactory)
    billing_payment_type = random.choice(PAYMENT_TYPE).key()
    rate_type = "default"
    member = factory.SubFactory(MemberFactory)
    emergency_contact = factory.SubFactory(MemberFactory)
    status = random.choice(Client.CLIENT_STATUS).keys()
    language = "en"
    alert = "This is an alert"
    delivery_type = "O"
    gender = "M"
    birthdate = factory.Faker('date')
