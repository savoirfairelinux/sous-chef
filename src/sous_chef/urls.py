"""sous-chef URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/

Examples:

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')

Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))

"""
from django.conf.urls import include, url
from django.contrib import admin


from page.views import HomeView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _

urlpatterns = i18n_patterns(
    url(
        _(r'^admin/'),
        admin.site.urls
    ),
    url(
        _(r'^meal/'),
        include('meal.urls', namespace="meal")
    ),
    url(
        _(r'^member/'),
        include('member.urls', namespace="member")
    ),
    url(
        _(r'^notification/'),
        include('notification.urls', namespace="notification")
    ),
    url(
        _(r'^order/'),
        include('order.urls', namespace="order")
    ),
    url(
        r'^p/',
        include('page.urls', namespace="page")
    ),
    url(r'^$', HomeView.as_view(), name='home'),
    url(
        _(r'^delivery/'),
        include('delivery.urls', namespace="delivery")
    ),
    url(
        _(r'^note/'),
        include('note.urls', namespace="note")
    ),
    url(
        _(r'^billing/'),
        include('billing.urls', namespace="billing")
    ),
    url(
        _(r'^avatar/'),
        include('avatar.urls')
        ),
    prefix_default_language=False
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
