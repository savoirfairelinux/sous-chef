from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from note.views import NoteList, NoteAdd, NoteBatchToggle

from note.views import mark_as_read, mark_as_unread

app_name = "note"

urlpatterns = [
    url(_(r'^$'), NoteList.as_view(), name='note_list'),
    url(_(r'^read/(?P<id>\d+)/$'),
        mark_as_read, name='read'),
    url(_(r'^unread/(?P<id>\d+)/$'),
        mark_as_unread, name='unread'),
    url(r'^add/$', NoteAdd.as_view(), name='note_add'),
    url(r'^batch_toggle/$',
        NoteBatchToggle.as_view(), name='batch_toggle'),
]
