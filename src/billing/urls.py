from django.conf.urls import url
from billing.views import (
    BillingList, BillingCreate, BillingDelete, BillingView
    )
from django.utils.translation import ugettext_lazy as _

urlpatterns = [
    url(r'^list/$', BillingList.as_view(), name="list"),
    url(r'^create/$', BillingCreate.as_view(), name="create"),
    url(r'^view/(?P<pk>\d+)/$', BillingView.as_view(), name="view"),
    url(r'^delete/(?P<pk>\d+)/$', BillingDelete.as_view(), name='delete'),
]
