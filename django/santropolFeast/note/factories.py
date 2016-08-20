# coding=utf-8
import factory
import random
from member.models import Client
from member.factories import ClientFactory
from note.models import Note
from django.contrib.auth.models import User


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda x: "user{}".format(x))


class NoteFactory(factory.DjangoModelFactory):

    class Meta:
        model = Note

    note = factory.Faker('sentence')
    author = factory.SubFactory(UserFactory)
    client = factory.SubFactory(ClientFactory)
    priority = factory.LazyAttribute(
        lambda x: random.choice(Note.PRIORITY_LEVEL)[0]
    )
