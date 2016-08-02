# coding=utf-8
import factory
import random
from member.models import Client
from member.factories import ClientFactory
from note.models import Note
from django.contrib.auth.models import User


class NoteFactory(factory.DjangoModelFactory):

    class Meta:
        model = Note

    note = factory.Faker('sentence')
    client = factory.SubFactory(ClientFactory)
    priority = factory.LazyAttribute(
        lambda x: random.choice(Note.PRIORITY_LEVEL)[0]
    )
