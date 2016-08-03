from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from order.views import OrderList, show_information, change_status

urlpatterns = [
    url(_(r'^list/$'), OrderList.as_view(), name='list'),
    url(_(r'^view/(?P<id>\d+)/$'), show_information, name='view'),
    url(_(r'^change_status/(?P<id>\d+)/$'),
        change_status, name='change_status'),
]
