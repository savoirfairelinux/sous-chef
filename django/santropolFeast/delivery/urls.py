from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from delivery.views import Orderlist, MealInformation, RoutesInformation
from delivery.views import kcr_view
from delivery.views import dailyOrders
from delivery.views import routeDailyOrders

urlpatterns = [
    url(_(r'^order/$'), Orderlist.as_view(), name='order'),
    url(_(r'^meal/$'), MealInformation.as_view(), name='meal'),
    url(_(r'^route/$'), RoutesInformation.as_view(), name='route'),
    url(_(r'^kitchen_count/$'), kcr_view, name='route'),
    url(_(r'^getDailyOrders/$'), dailyOrders, name='dailyOrders'),
    url(_(r'^getDailyOrders/route[0-9]{1}/$'), routeDailyOrders, name='routeDailyOrders'),
]
