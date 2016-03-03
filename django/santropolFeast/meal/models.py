from django.db import models
from django.utils.translation import ugettext_lazy as _


class Meal(models.Model):
    class Meta:
        verbose_name_plural = _('meals')

    # Meal information
    nom = models.CharField(max_length=50, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='related_meals'
    )


class Ingredient(models.Model):
    class Meta:
        verbose_name_plural = _('ingredients')

        # Ingredient information
        nom = models.CharField(max_length=50, verbose_name=_('name'))


class Allergy(models.Model):
    class Meta:
        verbose_name_plural = _('allergies')

    # Allergy information
    nom = models.CharField(max_length=50, verbose_name=_('name'))
    description = models.TextFields(verbose_name=_('description'))
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='related_allergies'
    )
