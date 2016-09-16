from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from delivery.views import (Orderlist, MealInformation, RoutesInformation,
                            KitchenCount, MealLabels, DeliveryRouteSheet)
from delivery.views import Orderlist, MealInformation, RoutesInformation
from delivery.views import dailyOrders, refreshOrders, saveRoute

urlpatterns = [
    url(_(r'^order/$'), Orderlist.as_view(), name='order'),
    url(_(r'^meal/$'), MealInformation.as_view(), name='meal'),
    url(_(r'^meal/(?P<id>\d+)/$'), MealInformation.as_view(), name='meal_id'),
    url(_(r'^route/$'), RoutesInformation.as_view(), name='route'),
    url(_(r'^kitchen_count/$'), KitchenCount.as_view(), name='kitchen_count'),
    url(_(r'^kitchen_count/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d+)/$'),
        KitchenCount.as_view(), name='kitchen_count_date'),
    url(_(r'^viewMealLabels/$'), MealLabels.as_view(), name='mealLabels'),
    url(_(r'^route_sheet/(?P<id>\d+)/$'),
        DeliveryRouteSheet.as_view(), name='route_sheet_id'),
    url(_(r'^getDailyOrders/$'), dailyOrders, name='dailyOrders'),
    url(_(r'^refresh_orders/$'), refreshOrders, name='refresh_orders'),
    url(_(r'^saveRoute/$'), saveRoute, name='saveRoute'),
]
