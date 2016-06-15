from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from order.views import show_order_information, OrderList

urlpatterns = [
    url(_(r'^view/(?P<id>\d+)/$'), show_order_information, name='view'),
    url(_(r'^list/$'), OrderList.as_view(), name='list')
]
