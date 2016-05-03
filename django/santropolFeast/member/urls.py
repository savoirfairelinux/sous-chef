from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from member.views import *

urlpatterns = patterns(
    '',
    url(_(r'^list/$'),
        ClientList.as_view(), name='list'),
)
