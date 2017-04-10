from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from delivery.views import (Orderlist, MealInformation, RoutesInformation,
                            KitchenCount, MealLabels, DeliveryRouteSheet,
                            RefreshOrderView, CreateDeliveryOfToday,
                            EditDeliveryOfToday)

app_name = "delivery"

urlpatterns = [
    url(_(r'^order/$'), Orderlist.as_view(), name='order'),
    url(_(r'^meal/$'), MealInformation.as_view(), name='meal'),
    url(_(r'^meal/(?P<id>\d+)/$'), MealInformation.as_view(), name='meal_id'),
    url(_(r'^routes/$'), RoutesInformation.as_view(), name='routes'),
    url(_(r'^route/(?P<pk>\d+)/$'),
        EditDeliveryOfToday.as_view(), name='edit_delivery_of_today'),
    url(_(r'^route/(?P<pk>\d+)/create/$'),
        CreateDeliveryOfToday.as_view(), name='create_delivery_of_today'),
    url(_(r'^kitchen_count/$'), KitchenCount.as_view(), name='kitchen_count'),
    url(_(r'^kitchen_count/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d+)/$'),
        KitchenCount.as_view(), name='kitchen_count_date'),
    url(_(r'^viewDownloadKitchenCount/$'),
        KitchenCount.as_view(), name='downloadKitchenCount'),
    url(_(r'^viewMealLabels/$'), MealLabels.as_view(), name='mealLabels'),
    url(_(r'^route_sheet/(?P<pk>\d+)/$'),
        DeliveryRouteSheet.as_view(), name='route_sheet'),
    url(_(r'^refresh_orders/$'),
        RefreshOrderView.as_view(), name='refresh_orders'),
]
