from django import template

register = template.Library()


@register.simple_tag(takes_context=True, name='cell')
def dish_day(context, meal, day):
    return context['wizard']["form"][meal+"_"+day+"_quantity"]


@register.simple_tag(takes_context=True, name="size")
def dish_size(context, day):
    return context['wizard']['form']["size_"+day]
