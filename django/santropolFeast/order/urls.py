from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from order.views import OrderList

urlpatterns = [
    url(_(r'^list/$'), OrderList.as_view(), name='list')
]
