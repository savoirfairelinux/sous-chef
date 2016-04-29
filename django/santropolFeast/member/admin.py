from django.contrib import admin
from member.models import Member, Client, Contact, Address, Profile

admin.site.register(Member)
admin.site.register(Client)
admin.site.register(Contact)
admin.site.register(Address)
admin.site.register(Profile)
