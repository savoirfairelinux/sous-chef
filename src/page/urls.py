from django.conf.urls import url
from page import views
from django.contrib.auth import views as auth_views

app_name = "page"

urlpatterns = [
    url(
        r'^home$',
        views.HomeView.as_view(),
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
