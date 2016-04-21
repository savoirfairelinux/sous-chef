# coding: utf-8

from django.contrib.auth import logout
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def logout_view(request):
    logout(request)
    messages.add_message(
        request,
        messages.WARNING,
        _('disconnected message')
    )
    # Redirect to a success page.
    return HttpResponseRedirect(reverse_lazy("page:home"))

def custom_login(request):
    if request.user.is_authenticated():
        # Redirect to home if already logged in.
        return HttpResponseRedirect(reverse_lazy("page:home"))
    else:
        return login(request)
    
@login_required
def home(request):
    return render(request, 'pages/home.html')
