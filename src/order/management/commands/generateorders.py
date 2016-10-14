from django.core.management.base import BaseCommand
from order.models import Order
from member.models import Client
from datetime import datetime
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE


class Command(BaseCommand):
    help = 'Create new orders for a given delivery date for all\
            ongoing active clients using their meals defaults.'

    def add_arguments(self, parser):
        parser.add_argument(
            'delivery_date',
            help='The date must be in the format YYYY-MM-DD',
        )

    def handle(self, *args, **options):
        delivery_date = datetime.strptime(
            options['delivery_date'], '%Y-%m-%d'
        ).date()

        # Only active clients can receive orders
        clients = Client.active.all()
        # Create the orders
        numorders = Order.objects.auto_create_orders(delivery_date, clients)
        # Log the execution
        LogEntry.objects.log_action(
            user_id=1, content_type_id=1,
            object_id="", object_repr="Orders creation for "+str(
                delivery_date.strftime('%Y-%m-%d %H:%M')),
            action_flag=ADDITION,
        )
        print("Orders created: ", numorders,
              "to be delivered on ", delivery_date, ".")
