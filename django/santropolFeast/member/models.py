from django.db import models
from django.utils.translation import ugettext_lazy as _

CONTACT_TYPE_CHOICES = (
	('Home phone', 1),
	('Cell phone', 2),
	('Work phone', 3),
	('Email', 4),
)


class Member(models.Model):
	class Meta:
		verbose_name_plural = _('Members')

	# Member information
	firstname = models.CharField(max_length=50, verbose_name=_('Firstname'))
	lastname = models.CharField(max_length=50, verbose_name=_('Lastname'))
	

class Address(models.Model):
	class meta:
		verbose_name_plural = _('Addresses')

	#Member address information
	number = models.CharField(max_length=50, verbose_name=_('Address number'))
	street = models.CharField(max_length=100, verbose_name=_('Street'))
	apartment = models.CharField(max_length=10, verbose_name=_('Apartment number'))
	floor= models.CharField(max_length=3, verbose_name=_('Floor number'))
	city = models.CharField(max_length=50, verbose_name=_('City'))
	postal_code = models.CharField(max_length=6, verbose_name=_('Postal code'))
	member = models.ForeignKey(Member, verbose_name=_('Member'))


class Contact(models.Model):
        class Meta:
                verbose_name_plural = _('Contacts')

        # Member contact information
        type = models.CharField(choices=CONTACT_TYPE_CHOICES, verbose_name=_('Contact type'))
	value = models.CharField(max_length=50, verbose_name=_('Value'))
        member = models.ForeignKey(Member, verbose_name=_('Member'))

class Client(models.Model):
	class Meta:
		verbose_name_plural = _('Clients')

	#Client information
        billing_address = models.ForeignKey(Address, verbose_name=_('Billing address'))	
        member = models.ForeignKey(Member, verbose_name=_('Member'))
        restrictions = models.ManyToManyField(Ingredient, related_name='restricted_clients'))
        allergies = models.ManyToManyField(Allergy, related_name='allergic_clients'))

