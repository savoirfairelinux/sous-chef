from django.conf.urls import url
from billing.views import (
    BillingList, BillingCreate, BillingDelete,
    BillingSummaryView, BillingOrdersView, BillingAdd
)
from django.utils.translation import ugettext_lazy as _

app_name = "billing"

urlpatterns = [
    url(_(r'^list/$'), BillingList.as_view(), name="list"),
    url(_(r'^create/$'), BillingCreate.as_view(), name="create"),
    url(_(r'^add/$'), BillingAdd.as_view(), name="add"),
    url(_(r'^view/(?P<pk>\d+)/$'),
        BillingSummaryView.as_view(), name="view"),
    url(_(r'^view/(?P<pk>\d+)/orders/$'),
        BillingOrdersView.as_view(), name="view_orders"),
    url(_(r'^delete/(?P<pk>\d+)/$'), BillingDelete.as_view(), name='delete'),
]
