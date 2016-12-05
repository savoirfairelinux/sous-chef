from django import template
from meal.models import COMPONENT_GROUP_CHOICES
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.simple_tag(takes_context=True, name='cell')
def dish_day(context, meal, day):
    return context["form"][meal + "_" + day + "_quantity"]


@register.simple_tag(takes_context=True, name="size")
def dish_size(context, day):
    return context['form']["size_" + day]


@register.filter
def readable_prefs(value):
    if value is None:
        return _("Not properly configured.")

    str = ''
    for component, label in COMPONENT_GROUP_CHOICES:
        count = value.get(component)
        if count:  # more than 0
            str += '{} {}, '.format(count, label)

    return str[:-2]


@register.filter
def get_item(o, key):
    return o[key]
