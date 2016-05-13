# Create your views here.
from django.views import generic
from notification.models import Notification


class NotificationList(generic.ListView):
    # Display the list of clients
    model = Notification
    template_name = 'list.html'
    context_object_name = 'notifications'
