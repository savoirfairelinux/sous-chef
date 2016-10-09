from django import template
from meal.models import COMPONENT_GROUP_CHOICES


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
        return ''

    str = ''
    for component, label in COMPONENT_GROUP_CHOICES:
        str += '{} {}, '.format(value.get(component, 0), label)

    return str[:-2]
