"""santropolFeast URL Configuration

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

from page.views import home

urlpatterns = [
    url(
        r'^admin/',
        admin.site.urls
    ),
    url(
        r'^meal/',
        include('meal.urls', namespace="meal")
    ),
    url(
        r'^member/',
        include('member.urls', namespace="member")
    ),
    url(
        r'^notification/',
        include('notification.urls', namespace="notification")
    ),
    url(
        r'^order/',
        include('order.urls', namespace="order")
    ),
    url(
        r'^p/',
        include('page.urls', namespace="page")
    ),
    url(r'^$', home, name='home'),
    url(
        r'^delivery/',
        include('delivery.urls', namespace="delivery")
    ),
    url(
        r'^note/',
        include('note.urls', namespace="note")
    ),
    url(
        r'^billing/', include('billing.urls', namespace="billing"))
]
