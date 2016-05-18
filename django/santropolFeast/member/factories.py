# coding=utf-8
import factory
import datetime
from django.contrib.auth.models import User
from santropolFeast.member.models import Member, Address, Contact, Client,\
    Profile


class MemberFactory (factory.DjangoModelFactory):

    class Meta:
        model = Member

    firstname = "VaÈËÇç"
    lastname = "ËÏÉéè"

    gender = 'U'
    birthday = datetime.datetime(1945, 4, 1)


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


class ContactFactory (factory.DjangoModelFactory):

    class Meta:
        model = Contact

    type = "Home Phone"
    value = "514-555-2556"

    @classmethod
    def __init__(self, **kwargs):
        member = kwargs.pop("member", MemberFactory())
        contact = super(ContactFactory, self).__init__(self, **kwargs)

        contact.save()


class ClientFactory (factory.DjangoModelFactory):

    class Meta:
        model = Client

    @classmethod
    def __init__(self, **kwargs):
        member = kwargs.pop("member", MemberFactory())
        billing_address = kwargs.pop(
            "billing_address",
            AddressFactory(member=member)
        )
        emergency_contact = kwargs.pop("emergency_contact", MemberFactory())


class ProfileFactory(factory.DjangoModelFactory):

    class Meta:
        model = Profile

    description = "Description of the user"

    @classmethod
    def __init__(self, **kwargs):
        user = kwargs.pop("user", None)


class AdminFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = "FactoryAdmin"
    password = "Toto1234!#"

    is_active = True

    is_staff = True

    is_superuser = True


class AdminProfileFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    user = AdminFactory()
