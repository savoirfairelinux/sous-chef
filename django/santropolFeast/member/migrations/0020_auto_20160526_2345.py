from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0019_auto_20160525_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referencing',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Referral date'),
        ),
    ]
