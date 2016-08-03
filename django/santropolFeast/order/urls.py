from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from order.views import (
    OrderList, show_information, delete_order_item, edit_order_information
)

urlpatterns = [
    url(_(r'^list/$'), OrderList.as_view(), name='list'),
    url(_(r'^view/(?P<id>\d+)/$'), show_information, name='view'),
    url(_(r'^view/delete/(?P<id>\d+)/$'),
        delete_order_item, name='delete_item'),
    url(_(r'^view/(?P<id>\d+)/edit/(?P<item_id>\d+)/$'),
        edit_order_information, name="edit_item")
]
