# coding=utf-8
import factory
import random
from member.factories import ClientFactory
from note.models import Note, NotePriority, NoteCategory
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
        lambda x: random.choice(NotePriority.objects.all()).pk
    )
    categories = factory.LazyAttribute(
        lambda x: random.choice(NoteCategory.objects.all()).pk
    )
