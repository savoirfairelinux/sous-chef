from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from member.views import (
    ClientWizard, NoteList, mark_as_read,
    show_information, ClientList, SearchMembers
)

from member.forms import (
    ClientBasicInformation, ClientAddressInformation,
    ClientReferentInformation, ClientPaymentInformation,
    ClientRestrictionsInformation, ClientEmergencyContactInformation
)

create_member_forms = (
    ('basic_information', ClientBasicInformation),
    ('address_information', ClientAddressInformation),
    ('referent_information', ClientReferentInformation),
    ('payment_information', ClientPaymentInformation),
    ('dietary_restriction', ClientRestrictionsInformation),
    ('emergency_contact', ClientEmergencyContactInformation),
)

member_wizard = ClientWizard.as_view(create_member_forms,
                                     url_name='member:member_step')

urlpatterns = [
    url(r'^create/$', member_wizard, name='member_step'),
    url(r'^create/(?P<step>.+)/$', member_wizard,
        name='member_step'),
    url(r'^list/$', ClientList.as_view(), name='list'),
    url(r'^search/$', SearchMembers.as_view(), name='search'),
    url(_(r'^notes/$'), NoteList.as_view(), name='notes'),
    url(_(r'^note/read/(?P<id>[0-9]{1})/$'),
        mark_as_read, name='read'),
    url(_(r'^view/(?P<id>\d+)/$'),
        show_information,
        name='view'),
]
