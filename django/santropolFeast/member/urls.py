from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from member.views import (
    ClientWizard, NoteList, client_list, mark_as_read,
    show_information
)

from member.forms import (
    ClientBasicInformation, ClientAddressInformation,
    ClientReferentInformation, ClientPaymentInformation,
    ClientRestrictionsInformation, ClientEmergencyContactInformation
)

create_member_forms = (
    ('basic_info', ClientBasicInformation),
    ('address_information', ClientAddressInformation),
    ('referent_information', ClientReferentInformation),
    ('payment_information', ClientPaymentInformation),
    ('dietary_restriction', ClientRestrictionsInformation),
    ('emergency_contact', ClientEmergencyContactInformation),
)

member_wizard = ClientWizard.as_view(create_member_forms,
                                     url_name='member:member_step')

urlpatterns = patterns('',
                       url(r'^create/$', member_wizard, name='member_step'),
                       url(r'^create/(?P<step>.+)/$', member_wizard,
                           name='member_step'),
                       url(r'^list/$', client_list, name='list'),
                       url(_(r'^notes/$'), NoteList.as_view(), name='notes'),
                       url(_(r'^note/read/(?P<id>[0-9]{1})/$'),
                           mark_as_read, name='read'),
                       url(_(r'^view_info/(?P<id>\d+)/$'),
                           show_information,
                           name='view_info'),
                       )
