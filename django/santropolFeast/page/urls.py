from django.conf.urls import patterns, url
from page import views

urlpatterns = patterns(
    '',
    url(
        r'^home$',
        views.home,
        name='home'
    ),
    url(
        r'^login$',
        'django.contrib.auth.views.login',
        name='login'
    ),
    url(
        r'^logout$',
        views.logout_view,
        name='logout'
    ),

)
