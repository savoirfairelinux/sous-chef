from django import template
from meal.models import COMPONENT_GROUP_CHOICES
from meal.settings import COMPONENT_SYSTEM_DEFAULT
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.filter(name='get_item')
def get_item(o, key):
    try:
        return o[key]
    except Exception:
        return None


@register.filter(name='alter_field_class')
def alter_field_class(field, css):
    return field.as_widget(attrs={"class": css})
