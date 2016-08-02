from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from order.views import (
    OrderList, OrderDetail, CreateOrder, UpdateOrder, UpdateOrderStatus
)
urlpatterns = [
    url(_(r'^list/$'), OrderList.as_view(), name='list'),
    url(_(r'^view/(?P<pk>\d+)/$'), OrderDetail.as_view(), name='view'),
    url(_(r'^create/$'), CreateOrder.as_view(), name='create'),
    url(_(r'^update/(?P<pk>\d+)/$'), UpdateOrder.as_view(), name='update'),
    url(
        _(r'^update/(?P<pk>\d+)/status$'),
        UpdateOrderStatus.as_view(),
        name='update_status'
    ),
]
