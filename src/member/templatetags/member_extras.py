from django import template
from meal.models import COMPONENT_GROUP_CHOICES
from meal.settings import COMPONENT_SYSTEM_DEFAULT
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
    if not value:
        # give a system default
        value = COMPONENT_SYSTEM_DEFAULT

    outputs = []
    for component, label in COMPONENT_GROUP_CHOICES:
        count = value.get(component)
        if count:  # more than 0
            if component == 'main_dish':
                size = value['size']
                size_s = 'Large' if size == 'L' else 'Regular'
                outputs.append(
                    _('%(count)s %(size)s %(component_label)s') %
                    {'count': count, 'size': size_s, 'component_label': label}
                )
            else:
                outputs.append(
                    _('%(count)s %(component_label)s') %
                    {'count': count, 'component_label': label}
                )

    return ', '.join(outputs)


@register.filter
def get_item(o, key):
    return o[key]
