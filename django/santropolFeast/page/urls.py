from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(
        r'^$',
        'django.contrib.auth.views.login',
        name='home'
    ),
)
