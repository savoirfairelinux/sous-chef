from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

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
    ClientStatusView,
    ClientStatusSchedulerDeleteView,
    ClientUpdateBasicInformation,
    ClientUpdateAddressInformation,
    ClientUpdateReferentInformation,
    ClientUpdatePaymentInformation,
    ClientUpdateDietaryRestriction,
    ClientUpdateEmergencyContactInformation,
    clientMealsPrefsAsJSON,
)

from member.forms import (
    ClientBasicInformation, ClientAddressInformation,
    ClientReferentInformation, ClientPaymentInformation,
    ClientRestrictionsInformation
)
from member.formsets import CreateEmergencyContactFormset

from note.views import ClientNoteList, ClientNoteListAdd

app_name = "member"

member_forms = ({
    'name':        'basic_information',
    'step_url':    _('basic_information'),
    'create_form': ClientBasicInformation,
    'update_form': ClientUpdateBasicInformation
}, {
    'name':        'address_information',
    'step_url':    _('address_information'),
    'create_form': ClientAddressInformation,
    'update_form': ClientUpdateAddressInformation
}, {
    'name':        'referent_information',
    'step_url':    _('referent_information'),
    'create_form': ClientReferentInformation,
    'update_form': ClientUpdateReferentInformation
}, {
    'name':        'payment_information',
    'step_url':    _('payment_information'),
    'create_form': ClientPaymentInformation,
    'update_form': ClientUpdatePaymentInformation,
}, {
    'name':        'dietary_restriction',
    'step_url':    _('dietary_restriction'),
    'create_form': ClientRestrictionsInformation,
    'update_form': ClientUpdateDietaryRestriction,
}, {
    'name':        'emergency_contacts',
    'step_url':    _('emergency_contacts'),
    'create_form': CreateEmergencyContactFormset,
    'update_form': ClientUpdateEmergencyContactInformation
})

member_wizard = ClientWizard.as_view(
    list(map(lambda d: (d['name'], d['create_form']), member_forms)),
    i18n_url_names=list(map(
        lambda d: (d['name'], d['step_url']), member_forms
    )),
    url_name='member:member_step'
)


urlpatterns = [
    url(_(r'^create/$'), member_wizard, name='member_step'),
    url(_(r'^create/(?P<step>.+)/$'), member_wizard,
        name='member_step'),
    url(_(r'^list/$'), ClientList.as_view(), name='list'),
    url(_(r'^search/$'), SearchMembers.as_view(), name='search'),
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
    url(_(r'^view/(?P<pk>\d+)/notes/add$'),
        ClientNoteListAdd.as_view(), name='client_notes_add'),
    url(_(r'^geolocateAddress/$'), geolocateAddress, name='geolocateAddress'),
    url(_(r'^view/(?P<pk>\d+)/status$'),
        ClientStatusView.as_view(), name='client_status'),
    url(_(r'^client/(?P<pk>\d+)/status/scheduler$'),
        ClientStatusScheduler.as_view(), name='clientStatusScheduler'),
    url(
        r'^status/(?P<pk>\d+)/delete$',
        ClientStatusSchedulerDeleteView.as_view(),
        name='delete_status'
    ),
    url(_(r'^restriction/(?P<pk>\d+)/delete/$'),
        DeleteRestriction.as_view(), name='restriction_delete'),
    url(_(r'^client_option/(?P<pk>\d+)/delete/$'),
        DeleteClientOption.as_view(), name='client_option_delete'),
    url(_(r'^ingredient_to_avoid/(?P<pk>\d+)/delete/$'),
        DeleteIngredientToAvoid.as_view(), name='ingredient_to_avoid_delete'),
    url(_(r'^component_to_avoid/(?P<pk>\d+)/delete/$'),
        DeleteComponentToAvoid.as_view(), name='component_to_avoid_delete'),

    url(_(r'^client/(?P<pk>\d+)/meals/preferences$'),
        clientMealsPrefsAsJSON, name='client_meals_pref'),

]

# Handle client update forms URL
for d in member_forms:
    urlpatterns.append(
        url(string_concat(_(r'^(?P<pk>\d+)/update/'), d['step_url'], '/$'),
            d['update_form'].as_view(),
            name='member_update_' + d['name'])
    )
