from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from delivery.models import Delivery


class Orderlist(generic.ListView):
    # Display all the order on a given day
    model = Delivery
    template_name = 'order.html'


class MealInformation(generic.ListView):
    # Display all the meal and alert for a given day
    model = Delivery
    template_name = 'information.html'


class RoutesInformation(generic.ListView):
    # Display all the route information for a given day
    model = Delivery
    template_name = "routes.html"
