from django.db import models
from django.db.models import Q
from django_filters import FilterSet, ChoiceFilter, BooleanFilter, MethodFilter
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class NoteManager(models.Manager):
    pass


class UnreadNoteManager(NoteManager):

    def get_queryset(self):

        return super(UnreadNoteManager, self).get_queryset().filter(
            is_read=0
        )


class Note (models.Model):

    PRIORITY_LEVEL_NORMAL = 'normal'
    PRIORITY_LEVEL_URGENT = 'urgent'

    PRIORITY_LEVEL = (
        (PRIORITY_LEVEL_NORMAL, _('Normal')),
        (PRIORITY_LEVEL_URGENT, _('Urgent')),
    )

    class Meta:
        verbose_name_plural = _('Notes')
        ordering = ('-date', 'note')

    note = models.TextField(
        verbose_name=_('Note')
    )

    author = models.ForeignKey(
        User,
        verbose_name=_('Author'),
        null=True,
    )

    date = models.DateField(
        verbose_name=_('Date'),
        default=timezone.now,
    )

    is_read = models.BooleanField(
        verbose_name=_('Is read'),
        default=False
    )

    client = models.ForeignKey(
        'member.Client',
        verbose_name=_('Client'),
        related_name='client_notes'
    )

    priority = models.CharField(
        max_length=15,
        choices=PRIORITY_LEVEL,
        default=PRIORITY_LEVEL_NORMAL
    )

    objects = NoteManager()

    unread = UnreadNoteManager()

    def __str__(self):
        return self.note

    def mark_as_read(self):
        """Mark a note as read."""
        if not self.is_read:
            self.is_read = True
            self.save()

    def mark_as_unread(self):
        """Mark a note as nread."""
        if self.is_read:
            self.is_read = False
            self.save()


class NoteFilter(FilterSet):

    IS_READ_CHOICES = (
        ('', 'All'),
        ('1', 'Yes'),
        ('0', 'No'),
    )

    priority = ChoiceFilter(
        choices=(('', ''),) + Note.PRIORITY_LEVEL,
    )

    is_read = ChoiceFilter(
        choices=IS_READ_CHOICES,
    )

    name = MethodFilter(
        action='filter_search',
        label=_('Search by name')
    )

    class Meta:
        model = Note
        fields = ['priority', 'is_read']

    @staticmethod
    def filter_search(queryset, value):
        if not value:
            return queryset

        names = value.split(' ')

        name_contains = Q()

        for name in names:
            firstname_contains = Q(
                client__member__firstname__icontains=name
            )

            name_contains |= firstname_contains

            lastname_contains = Q(
                client__member__lastname__icontains=name
            )
            name_contains |= lastname_contains

        return queryset.filter(
            name_contains
        )
