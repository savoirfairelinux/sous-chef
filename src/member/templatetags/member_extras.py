from django import template

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
    for component in [
            'main_dish',
            'compote',
            'dessert',
            'fruit_salad',
            'green_salad',
            'pudding']:
        str += '{} {}, '.format(value[component], component)

    return str
