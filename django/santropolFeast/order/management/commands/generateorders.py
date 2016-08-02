from django.core.management.base import BaseCommand
from order.models import Order
from member.models import Client
from meal.factories import MenuFactory
from datetime import datetime
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE


class Command(BaseCommand):
    help = 'Generate orders for all clients using his preferences'

    def add_arguments(self, parser):
        parser.add_argument(
            '--creation_date',
            help='The date must be in the format YYYY-MM-DD',
        )
        parser.add_argument(
            'delivery_date',
            help='The date must be in the format YYYY-MM-DD',
        )

    def handle(self, *args, **options):
        if options['creation_date']:
            creation_date = datetime.strptime(
                options['creation_date'], '%Y-%m-%d'
            ).date()
        else:
            creation_date = datetime.now().date()
        delivery_date = datetime.strptime(
            options['delivery_date'], '%Y-%m-%d'
        ).date()
        clients = Client.active.all()
        numorders = Order.create_orders_on_defaults(
            creation_date, delivery_date, clients)
        LogEntry.objects.log_action(
            user_id=1, content_type_id=1,
            object_id="", object_repr="Generation of order for "+str(
                datetime.now().strftime('%Y-%m-%d %H:%M')),
            action_flag=ADDITION,
        )
        print("On", creation_date,
              "created", numorders,
              "orders to be delivered on", delivery_date, ".")
