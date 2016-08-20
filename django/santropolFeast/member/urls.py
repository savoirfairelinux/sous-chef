from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from member.views import (
    ClientWizard,
    ClientDetail,
    ClientList,
    SearchMembers,
    ClientOrderList,
    ClientInfoView,
    ClientReferentView,
    ClientPaymentView,
    ClientAllergiesView,
    DeleteRestriction,
    DeleteClientOption,
    DeleteIngredientToAvoid,
    DeleteComponentToAvoid,
    geolocateAddress,
    ClientStatusScheduler,
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
    url(r'^client/(?P<pk>\d+)/status/scheduler$',
        ClientStatusScheduler.as_view(), name='clientStatusScheduler'),
    url(_(r'^restriction/(?P<pk>\d+)/delete/$'),
        DeleteRestriction.as_view(), name='restriction_delete'),
    url(_(r'^client_option/(?P<pk>\d+)/delete/$'),
        DeleteClientOption.as_view(), name='client_option_delete'),
    url(_(r'^ingredient_to_avoid/(?P<pk>\d+)/delete/$'),
        DeleteIngredientToAvoid.as_view(), name='ingredient_to_avoid_delete'),
    url(_(r'^component_to_avoid/(?P<pk>\d+)/delete/$'),
        DeleteComponentToAvoid.as_view(), name='component_to_avoid_delete'),

]
