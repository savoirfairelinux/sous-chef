from django.contrib import admin
from member.models import Member, Client, Contact, Address, Note, Referencing
from member.models import Route

admin.site.register(Member)
admin.site.register(Client)
admin.site.register(Route)
admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Note)
admin.site.register(Referencing)
