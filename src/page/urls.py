from django.conf.urls import url
from page import views
from django.contrib.auth import views as auth_views

urlpatterns = [
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
        auth_views.logout,
        {'next_page': '/'},
        name='logout'
    ),
]
