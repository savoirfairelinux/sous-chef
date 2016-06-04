from django.conf.urls import patterns, url
from delivery import views

urlpatterns = patterns('',
                       #url(r'^distance$', views.show_distance),
                       url(r'^distance$', views.show_distance, name='show_distance'),
                       )
