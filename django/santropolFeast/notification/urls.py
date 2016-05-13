from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from notification.views import NotificationList

urlpatterns = patterns(
    '',
    url(_(r'^list/$'),
        NotificationList.as_view(), name='list'),
)
