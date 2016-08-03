from django.conf.urls import url
from member.views import geolocateAddress
from django.utils.translation import ugettext_lazy as _

from member.views import (
    ClientWizard,
    ClientDetail, ClientList, SearchMembers,
    ClientOrderList, ClientInfoView, ClientReferentView, ClientPaymentView,
    ClientAllergiesView,
)

from member.forms import (
    ClientBasicInformation, ClientAddressInformation,
    ClientReferentInformation, ClientPaymentInformation,
    ClientRestrictionsInformation, ClientEmergencyContactInformation
)

from note.views import ClientNoteList

create_member_forms = (
    ('basic_information', ClientBasicInformation),
    ('address_information', ClientAddressInformation),
    ('referent_information', ClientReferentInformation),
    ('payment_information', ClientPaymentInformation),
    ('dietary_restriction', ClientRestrictionsInformation),
    ('emergency_contact', ClientEmergencyContactInformation)
)

member_wizard = ClientWizard.as_view(create_member_forms,
                                     url_name='member:member_step')

urlpatterns = [
    url(r'^create/$', member_wizard, name='member_step'),
    url(r'^create/(?P<step>.+)/$', member_wizard,
        name='member_step'),
    url(r'^list/$', ClientList.as_view(), name='list'),
    url(r'^search/$', SearchMembers.as_view(), name='search'),
    url(_(r'^view/(?P<pk>\d+)/$'), ClientDetail.as_view(), name='view'),
    url(_(r'^view/(?P<pk>\d+)/orders$'),
        ClientOrderList.as_view(), name='list_orders'),
    url(_(r'^view/(?P<pk>\d+)/information$'),
        ClientInfoView.as_view(), name='client_information'),
    url(_(r'^view/(?P<pk>\d+)/referent$'),
        ClientReferentView.as_view(), name='client_referent'),
    url(_(r'^view/(?P<pk>\d+)/billing$'),
        ClientPaymentView.as_view(), name='client_payment'),
    url(_(r'^view/(?P<pk>\d+)/preferences$'),
        ClientAllergiesView.as_view(), name='client_allergies'),
    url(_(r'^view/(?P<pk>\d+)/notes$'),
        ClientNoteList.as_view(), name='client_notes'),
    url(_(r'^geolocateAddress/$'), geolocateAddress, name='geolocateAddress'),
]
