from django.core.management.base import BaseCommand
from order.models import Order, ORDER_STATUS_ORDERED, ORDER_STATUS_DELIVERED
from datetime import datetime
from django.contrib.admin.models import LogEntry, ADDITION


class Command(BaseCommand):
    help = 'Set status to Delivered for all orders that have the status\
            Ordered for the specified delivery date.'

    def add_arguments(self, parser):
        parser.add_argument(
            'delivery_date',
            help='The date must be in the format YYYY-MM-DD',
        )

    def handle(self, *args, **options):
        delivery_date = datetime.strptime(
            options['delivery_date'], '%Y-%m-%d'
        ).date()

        orders = Order.objects.filter(
            status=ORDER_STATUS_ORDERED,
            delivery_date=delivery_date)
        for order in orders:
            order.status = ORDER_STATUS_DELIVERED
            order.save()

        # Log the execution
        LogEntry.objects.log_action(
            user_id=1, content_type_id=1,
            object_id="",
            object_repr="Status set to delivered for orders on" + str(
                delivery_date.strftime('%Y-%m-%d %H:%M')),
            action_flag=ADDITION,
        )
        print("Status set to Delivered for {0} orders whose "
              "delivery date is {1}.".format(len(orders), delivery_date))
