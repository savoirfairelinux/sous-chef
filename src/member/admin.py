from django.contrib import admin
from member.models import (Member, Client, Contact, Address,
                           Referencing, Route, Client_avoid_component,
                           Client_avoid_ingredient, Option,
                           Client_option, Restriction)

admin.site.register(Member)
admin.site.register(Client)
admin.site.register(Route)
admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Referencing)
admin.site.register(Client_avoid_component)
admin.site.register(Client_avoid_ingredient)
admin.site.register(Option)
admin.site.register(Client_option)
admin.site.register(Restriction)
