from django.db import models
from django.db.models import Q
from django_filters import ChoiceFilter, DateFilter, FilterSet, CharFilter
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


class NotePriority(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('Name'))

    class Meta:
        verbose_name_plural = _('Note priorities')
        ordering = ('name',)

    def __str__(self):
        return u"%s" % self.name


class NoteCategory(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('Name'))

    class Meta:
        verbose_name_plural = _('Note categories')
        ordering = ('name',)

    def __str__(self):
        return u"%s" % self.name


class Note(models.Model):

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
        on_delete=models.SET_NULL
    )

    date = models.DateTimeField(
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
        related_name='client_notes',
        on_delete=models.CASCADE
    )

    priority = models.ForeignKey(
        NotePriority,
        verbose_name=_('Priority'),
        related_name="notes",
        null=True,
        on_delete=models.SET_NULL
    )

    category = models.ForeignKey(
        NoteCategory,
        verbose_name=_('Category'),
        related_name="notes",
        null=True,
        on_delete=models.SET_NULL
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

    NOTE_STATUS_UNREAD = IS_READ_CHOICES[2][0]

    is_read = ChoiceFilter(
        choices=IS_READ_CHOICES,
    )

    name = CharFilter(
        method='filter_search',
        label=_('Search by name')
    )

    date = DateFilter(lookup_expr='contains')

    class Meta:
        model = Note
        fields = ['priority', 'is_read', 'date', 'category', ]

    def filter_search(self, queryset, field_name, value):
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
