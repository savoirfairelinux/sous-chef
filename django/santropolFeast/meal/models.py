from django.db import models
from django.utils.translation import ugettext_lazy as _

class Meal(models.Model):
	class Meta:
		verbose_name_plural = _('Meals')

	#Meal information
	nom = models.CharField(max_length=50, verbose_name=_('Name'))
	description = models.TextFields(verbose_name=_('Description'))
	ingredients = models.ManyToManyField(Ingredient, related_name='related_meals'))

class Ingredient(models.Model):
        class Meta:
                verbose_name_plural = _('Ingredients')

        #Ingredient information
        nom = models.CharField(max_length=50, verbose_name=_('Name'))


class Allergy(models.Model):
        class Meta:
                verbose_name_plural = _('Allergies')

        #Allergy information
        nom = models.CharField(max_length=50, verbose_name=_('Name'))
        description = models.TextFields(verbose_name=_('Description'))
        ingredients = models.ManyToManyField(Ingredient, related_name='related_allergies'))
