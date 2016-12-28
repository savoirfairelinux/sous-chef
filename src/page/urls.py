from django.conf.urls import url
from page import views
from django.contrib.auth import views as auth_views
from django.utils.translation import ugettext_lazy as _

app_name = "page"

urlpatterns = [
    url(
        _(r'^home$'),
        views.HomeView.as_view(),
        name='home'
    ),
    url(
        _(r'^login$'),
        views.custom_login,
        name='login'
    ),
    url(
        _(r'^logout$'),
        auth_views.logout,
        {'next_page': '/'},
        name='logout'
    ),
]
