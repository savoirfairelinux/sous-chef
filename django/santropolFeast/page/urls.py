from django.conf.urls import patterns, url
from page import views
from django.contrib.auth import views as auth_views

urlpatterns = patterns(
    '',
    url(
        r'^home$',
        views.home,
        name='home'
    ),
    url(
        r'^login$',
        views.custom_login,
        name='login'
    ),
    url(
        r'^logout$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='logout'
    ),

)
