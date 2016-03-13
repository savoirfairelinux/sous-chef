# coding=utf-8
import factory
from santropolFeast.member.models import Member,Address,Contact,Client


class MemberFactory (factory.DjangoModelFactory):
    class Meta:
        model = Member

    firstname = "VaÈËÇç"
    lastname = "ËÏÉéè"


class AdressFactory (factory.DjangoModelFactory):
    class Meta:
        model = Address

    number = "5555"
    street = "rue de la montagne"
    apartment = "234A"
    floor = "22"
    city = "Montréal"
    postal_code = "H3C2C2"
    Member = MemberFactory


class ContactFactory (factory.DjangoModelFactory):
    class Meta:
        model = Contact

    type = "Home Phone"
    value = "514-555-2556"
    Member = MemberFactory


class ClientFactory (factory.DjangoModelFactory):
    class Meta:
        model = Client

