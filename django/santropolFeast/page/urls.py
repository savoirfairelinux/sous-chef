from django.conf.urls import patterns, url
from page import views

urlpatterns = patterns(
    '',
    url(
        r'^$',
        'django.contrib.auth.views.login',
        name='home'
    ),
    url(
        r'^logout$',
        views.logout_view,
        name='logout'
    ),
)
