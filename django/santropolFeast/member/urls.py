from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from member.views import *

urlpatterns = patterns(
    '',
    url(_(r'^clients/$'),
        ClientList.as_view(), name='client_list'),
)
